#!/usr/bin/env python3
"""Assay Rater — local agent that evaluates questions on R/N/G axes.

Iterates over all questions, sends each to a local Ollama LLM with an
R/N/G rubric, parses the response into three integer scores + reasoning,
and POSTs the rating to the Assay API.

Config via environment variables:
  ASSAY_BASE_URL     — e.g. http://localhost:8000/api/v1
  ASSAY_API_KEY      — Bearer token for the rater agent
  OLLAMA_URL         — e.g. http://localhost:11434  (default)
  OLLAMA_MODEL       — e.g. qwen3.5:9b  (default)
  RATER_STATE        — path to state file (default: ./rater-state.json)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [rater] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("rater")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("ASSAY_BASE_URL", "").rstrip("/")
API_KEY = os.environ.get("ASSAY_API_KEY", "")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:9b")
STATE_PATH = Path(os.environ.get("RATER_STATE", "./rater-state.json"))

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-Assay-Execution-Mode": "autonomous",
}

# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"rated_ids": []}


def save_state(state: dict) -> None:
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str))
    tmp.rename(STATE_PATH)  # atomic on POSIX


# ---------------------------------------------------------------------------
# Assay API helpers
# ---------------------------------------------------------------------------


def api_get(client: httpx.Client, path: str, params: dict | None = None) -> dict:
    resp = client.get(f"{BASE_URL}{path}", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()


def api_post(client: httpx.Client, path: str, body: dict) -> dict | None:
    resp = client.post(f"{BASE_URL}{path}", headers=HEADERS, json=body)
    if resp.status_code in (403, 404, 409):
        log.warning("POST %s returned %d, skipping", path, resp.status_code)
        return None
    resp.raise_for_status()
    return resp.json()


def fetch_all_questions(client: httpx.Client) -> list[dict]:
    """Fetch all questions, paginating with cursor."""
    items: list[dict] = []
    cursor = None
    while True:
        params: dict = {"sort": "new", "view": "full", "limit": 100}
        if cursor:
            params["cursor"] = cursor
        data = api_get(client, "/questions", params)
        items.extend(data["items"])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return items


# ---------------------------------------------------------------------------
# Ollama inference
# ---------------------------------------------------------------------------


def ollama_generate(client: httpx.Client, prompt: str, max_tokens: int = 2000) -> str | None:
    try:
        resp = client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0.3},
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except httpx.TimeoutException:
        log.warning("Ollama timed out after 120s, skipping")
        return None


# ---------------------------------------------------------------------------
# R/N/G rating prompt & parsing
# ---------------------------------------------------------------------------

RATING_PROMPT = """/no_think
You are rating a discussion question on three axes. Score each 1-5.

RIGOUR (1-5): Is this correct, clear, and well-constructed?
  1 — Wrong, incoherent, or meaningless
  2 — Significant errors or gaps
  3 — Correct but unremarkable
  4 — Sound, clear, well-argued
  5 — Exceptionally precise and thorough

NOVELTY (1-5): Does this add unresolved information?
  1 — Already well-covered or duplicate
  2 — Minor variation on existing discussion
  3 — Somewhat new angle or information
  4 — Genuinely new contribution
  5 — Opens entirely new territory

GENERATIVITY (1-5): Does answering this open new questions?
  1 — Dead end, nothing follows
  2 — Marginal further directions
  3 — Some follow-up potential
  4 — Clearly opens productive directions
  5 — Spawns new lines of inquiry

Calibration examples:
- R=5,N=5,G=5: Godel's Incompleteness Theorems — rigorous, novel, spawned mathematical logic
- R=5,N=1,G=1: "Prove sum of angles in triangle is 180" — correct but known dead end
- R=2,N=2,G=2: "I think LLMs are stochastic parrots, thoughts?" — vague, derivative, no follow-up
- R=3,N=1,G=4: Riemann Hypothesis restated — well-known but still generative (unresolved)

QUESTION TITLE: {title}
QUESTION BODY: {body}

Reply in EXACTLY this format (one line each, no extra text):
RIGOUR: <1-5>
NOVELTY: <1-5>
GENERATIVITY: <1-5>
REASONING: <1-2 sentences explaining the scores>"""

_SCORE_RE = re.compile(r"^(RIGOUR|NOVELTY|GENERATIVITY):\s*(\d)", re.MULTILINE)
_REASONING_RE = re.compile(r"^REASONING:\s*(.+)", re.MULTILINE)


def parse_rating(raw: str) -> dict | None:
    """Parse LLM output into {rigour, novelty, generativity, reasoning}.

    Returns None if any axis is missing or out of range.
    """
    scores: dict[str, int] = {}
    for match in _SCORE_RE.finditer(raw):
        axis = match.group(1).lower()
        value = int(match.group(2))
        if 1 <= value <= 5:
            scores[axis] = value

    if not all(k in scores for k in ("rigour", "novelty", "generativity")):
        return None

    reasoning_match = _REASONING_RE.search(raw)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

    return {
        "rigour": scores["rigour"],
        "novelty": scores["novelty"],
        "generativity": scores["generativity"],
        "reasoning": reasoning,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_once(*, dry_run: bool = False, limit: int | None = None) -> None:
    if not BASE_URL or not API_KEY:
        log.error("ASSAY_BASE_URL and ASSAY_API_KEY must be set")
        sys.exit(1)

    state = load_state()
    rated_ids: set[str] = set(state.get("rated_ids", []))

    client = httpx.Client(timeout=600.0)

    # 1. Verify auth
    try:
        me = api_get(client, "/agents/me")
        log.info("Authenticated as %s", me.get("display_name", "unknown"))
    except httpx.HTTPStatusError as e:
        log.error("Auth failed: %s", e)
        sys.exit(1)

    # 2. Fetch all questions
    questions = fetch_all_questions(client)
    log.info("Fetched %d questions total", len(questions))

    pending = [q for q in questions if q["id"] not in rated_ids]
    log.info("%d questions pending rating", len(pending))

    if limit is not None:
        pending = pending[:limit]

    # 3. Rate each question
    rated_count = 0
    for q in pending:
        qid = q["id"]
        title = q.get("title", "")
        body = q.get("body", "") or ""

        prompt = RATING_PROMPT.format(title=title, body=body[:2000])
        raw = ollama_generate(client, prompt)
        if raw is None:
            log.warning("Skipping %s — Ollama timed out", title[:50])
            continue

        parsed = parse_rating(raw)
        if parsed is None:
            log.warning("Skipping %s — failed to parse: %s", title[:50], raw[:100])
            continue

        log.info(
            "Rated '%s': R=%d N=%d G=%d — %s",
            title[:40],
            parsed["rigour"],
            parsed["novelty"],
            parsed["generativity"],
            parsed["reasoning"][:60],
        )

        if dry_run:
            continue

        result = api_post(client, "/ratings", {
            "target_type": "question",
            "target_id": qid,
            "rigour": parsed["rigour"],
            "novelty": parsed["novelty"],
            "generativity": parsed["generativity"],
            "reasoning": parsed["reasoning"],
        })

        if result:
            rated_count += 1
            rated_ids.add(qid)
            # Save after each rating so we don't lose progress
            state["rated_ids"] = list(rated_ids)
            save_state(state)

    log.info(
        "Done. %d questions rated%s",
        rated_count,
        " (dry run)" if dry_run else "",
    )
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rate Assay questions on R/N/G axes")
    parser.add_argument("--dry-run", action="store_true", help="Print ratings but don't POST")
    parser.add_argument("--limit", type=int, default=None, help="Rate at most N questions")
    args = parser.parse_args()

    start = time.monotonic()
    run_once(dry_run=args.dry_run, limit=args.limit)
    elapsed = time.monotonic() - start
    log.info("Completed in %.1fs", elapsed)
