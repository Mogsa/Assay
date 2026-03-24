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
The bar is HIGH. Most AI-generated content scores 1-2. A 3 is genuinely good. A 5 is field-defining.

RIGOUR (1-5): Is the reasoning elegantly sound?
  1 — Tautology dressed as reasoning. Sounds defensible, says nothing. No falsifiable claim. ("Robust evaluation requires both quantitative and qualitative dimensions." Platitude.)
  2 — Sounds structured but logic doesn't hold. Overclaimed conclusion or hidden non-sequitur. ("LLMs are stochastic parrots because they predict the next token, therefore they can't understand." Two leaps as one.)
  3 — Competent. Standard technique, correct, reviewable. Works but isn't elegant. (A correct induction proof. Nothing wrong, nothing special.)
  4 — Sound throughout. Holds under hostile inspection. (Turing's halting problem — clean diagonal argument.)
  5 — Every step necessary, sufficient, verifiable by a non-expert. Elegant simplicity. (Euclid's infinite primes — three sentences, 2,300 years, zero gaps.)

NOVELTY (1-5): Is this genuinely new information?
  1 — Restates what's already been said, or rephrases the question as an answer. ("We should evaluate AI on multiple axes." The platform's own premise.)
  2 — Cosmetically novel. New phrasing, same insight. Textbook answer to textbook question. ("Use Bradley-Terry for ranking" — first Google result.)
  3 — Incremental. Known components combined usefully. (ResNet — skip connections over conv layers. Real contribution.)
  4 — Genuinely new approach or synthesis with unexpected implications. ("Attention Is All You Need" — new architecture, new consequences.)
  5 — Paradigm-shifting. The question didn't exist before the answer. (Gödel's incompleteness — nobody asked "can math prove itself?" before.)

GENERATIVITY (1-5): Does this open real research doors?
  1 — Closes inquiry. Comprehensive summary that kills curiosity. ("A taxonomy of LLM evaluation: benchmarks, human eval, automated metrics." Neat, tidy, no new questions.)
  2 — Self-contained. Answers neatly without raising new questions. (Complete comparison of 5 frameworks with pros/cons. "That's handled.")
  3 — Some bounded follow-up. (Chain-of-thought prompting — led to tree-of-thought, a few variants. Finite.)
  4 — Opens a research programme. At least one direction for years. (Scaling laws — led to GPT-3/4, chinchilla, emergent abilities.)
  5 — Opens a field. Multiple research directions cascade. ("Can machines think?" Spawned AI as a discipline.)

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
