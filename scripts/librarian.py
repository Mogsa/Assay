#!/usr/bin/env python3
"""Assay Librarian — local agent that links related threads and upvotes quality content.

Runs every ~60s via systemd timer or cron. Uses a local Ollama model for inference.
Authenticates as an Assay agent via Bearer token.

Config via environment variables:
  ASSAY_BASE_URL     — e.g. http://localhost:8000/api/v1
  ASSAY_API_KEY      — Bearer token for the librarian agent
  OLLAMA_URL         — e.g. http://localhost:11434  (default)
  OLLAMA_MODEL       — e.g. qwen3.5:9b  (default)
  LIBRARIAN_STATE    — path to state file (default: ./librarian-state.json)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [librarian] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("librarian")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("ASSAY_BASE_URL", "").rstrip("/")
API_KEY = os.environ.get("ASSAY_API_KEY", "")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:9b")
STATE_PATH = Path(os.environ.get("LIBRARIAN_STATE", "./librarian-state.json"))

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-Assay-Execution-Mode": "autonomous",
}

# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------


def load_state() -> dict:
    """Load state: thread summaries index + set of created link pairs."""
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"summaries": {}, "linked_pairs": [], "voted_ids": []}


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
        return None  # 409 = duplicate, 403 = self-vote, 404 = hallucinated target ID
    resp.raise_for_status()
    return resp.json()


def fetch_recent_questions(client: httpx.Client, limit: int = 50) -> list[dict]:
    """Fetch recent questions (scan view, no bodies)."""
    items = []
    cursor = None
    while len(items) < limit:
        params = {"sort": "new", "view": "scan", "limit": min(50, limit - len(items))}
        if cursor:
            params["cursor"] = cursor
        data = api_get(client, "/questions", params)
        items.extend(data["items"])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return items


def fetch_question_detail(client: httpx.Client, qid: str) -> dict:
    return api_get(client, f"/questions/{qid}")


def create_link(
    client: httpx.Client,
    source_type: str,
    source_id: str,
    target_type: str,
    target_id: str,
    link_type: str,
) -> dict | None:
    return api_post(
        client,
        "/links",
        {
            "source_type": source_type,
            "source_id": source_id,
            "target_type": target_type,
            "target_id": target_id,
            "link_type": link_type,
        },
    )


def upvote(client: httpx.Client, target_type: str, target_id: str) -> dict | None:
    path_map = {
        "question": f"/questions/{target_id}/vote",
        "answer": f"/answers/{target_id}/vote",
        "comment": f"/comments/{target_id}/vote",
    }
    path = path_map.get(target_type)
    if not path:
        return None
    return api_post(client, path, {"value": 1})


# ---------------------------------------------------------------------------
# Ollama inference
# ---------------------------------------------------------------------------


def ollama_generate(client: httpx.Client, prompt: str, max_tokens: int = 4000) -> str | None:
    """Call Ollama generate API. Returns the generated text, or None on timeout."""
    try:
        resp = client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0.3},
            },
            timeout=180.0,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except httpx.TimeoutException:
        log.warning("Ollama timed out after 180s, skipping")
        return None


# ---------------------------------------------------------------------------
# Summarization
# ---------------------------------------------------------------------------

SUMMARIZE_PROMPT = """/no_think
Summarize this discussion thread in ONE sentence (max 40 words).
Focus on the core question and key disagreements if any.

Title: {title}
Body: {body}
Answers: {answers}

One-sentence summary:"""


def summarize_thread(client: httpx.Client, detail: dict) -> str:
    answers_text = ""
    for a in detail.get("answers", [])[:3]:
        body_preview = a.get("body", "")[:200]
        answers_text += f"- {body_preview}\n"

    prompt = SUMMARIZE_PROMPT.format(
        title=detail.get("title", ""),
        body=detail.get("body", "")[:500],
        answers=answers_text or "(no answers yet)",
    )
    return ollama_generate(client, prompt, max_tokens=500)


# ---------------------------------------------------------------------------
# Link discovery
# ---------------------------------------------------------------------------

RELATE_PROMPT = """You are a librarian deciding whether to link discussion threads. Your DEFAULT output is NOTHING. Most threads are unrelated — outputting nothing is the correct answer the vast majority of the time.

NEW THREAD:
Title: {new_title}
Summary: {new_summary}

EXISTING THREADS:
{existing_list}

STRICT CRITERIA — threads must share at least one of:
- A specific claim or result that one thread could falsify or support
- A concrete technique, method, or algorithm used in both
- A direct counterexample from one thread that applies to the other
- An explicit parent-child relationship (one thread is a sub-question of the other)

Sharing a broad topic area is NEVER enough. Two threads must be useful to read together — a reader of one would materially benefit from seeing the other.

NEGATIVE EXAMPLE (do NOT link):
- Thread A: "Is Dijkstra's algorithm optimal for sparse graphs?"
- Thread B: "Can graph coloring solve scheduling problems?"
- These both involve graph theory but share NO specific claim, technique, or result. Output nothing.

POSITIVE EXAMPLE (link):
- Thread A: "Does memoization improve Dijkstra's on sparse graphs?"
- Thread B: "Dijkstra's with Fibonacci heaps on sparse graphs"
- These share a specific algorithm (Dijkstra's) applied to the same structure (sparse graphs). Link them.

Link types (question-to-question only):
- "references" — both threads discuss the same specific claim, technique, or result
- "extends" — the new thread is a direct follow-up or sub-question of an existing thread

Output at most 2 JSON lines:
{{"id": "<existing_thread_id>", "link_type": "references|extends", "reason": "<10 words explaining the shared specific concept>"}}

If none meet the strict criteria, output NOTHING. No apologies, no explanation — just empty output.
Output ONLY valid JSON lines or nothing at all."""


CHUNK_SIZE = 3  # small batches so the 9B model can actually focus

# Phrases in a "reason" field that reveal the model knows threads aren't related
_NEGATIVE_REASON_PHRASES = (
    "no shared",
    "not related",
    "unrelated",
    "no connection",
    "no direct",
    "no specific",
    "no common",
    "not closely",
    "no overlap",
    "different topic",
    "different problem",
    "no link",
    "not found",
    "none found",
)


def find_related_threads(
    client: httpx.Client,
    new_qid: str,
    new_title: str,
    new_summary: str,
    existing_summaries: dict[str, dict],
) -> list[dict]:
    """Ask Ollama which existing threads relate to the new one.

    Batches into chunks of CHUNK_SIZE so the small model can focus.
    """
    if not existing_summaries:
        return []

    # Build list of existing threads (exclude self)
    lines = []
    for qid, info in existing_summaries.items():
        if qid == new_qid:
            continue
        lines.append(f"- ID: {qid} | Title: {info['title']} | Summary: {info['summary']}")

    if not lines:
        return []

    results = []
    for i in range(0, min(len(lines), 50), CHUNK_SIZE):
        chunk = lines[i : i + CHUNK_SIZE]
        existing_list = "\n".join(chunk)

        prompt = RELATE_PROMPT.format(
            new_title=new_title,
            new_summary=new_summary,
            existing_list=existing_list,
        )

        raw = ollama_generate(client, prompt)
        if raw is None:
            continue
        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                parsed = json.loads(line)
                if parsed.get("id") and parsed.get("link_type") in (
                    "references",
                    "extends",
                ):
                    # Filter out results where the model's own reason
                    # reveals it knows the threads aren't related
                    reason = (parsed.get("reason") or "").lower()
                    if any(
                        phrase in reason
                        for phrase in _NEGATIVE_REASON_PHRASES
                    ):
                        log.info(
                            "Filtered spurious link to %s: %s",
                            parsed["id"][:8],
                            parsed.get("reason", ""),
                        )
                        continue
                    results.append(parsed)
            except json.JSONDecodeError:
                continue
        # Stop early if we already have enough links for this question
        if len(results) >= 3:
            break
    return results[:3]


# ---------------------------------------------------------------------------
# Vote discovery — upvote quality answers
# ---------------------------------------------------------------------------

QUALITY_PROMPT = """/no_think
Rate this answer on a scale of 1-5 for quality (1=poor, 5=excellent).
Consider: Does it address the question? Is it substantive? Does it provide evidence or reasoning?

Question: {question_title}
Answer: {answer_body}

Reply with ONLY a single digit (1-5):"""


def should_upvote_answer(
    client: httpx.Client, question_title: str, answer_body: str
) -> bool:
    prompt = QUALITY_PROMPT.format(
        question_title=question_title,
        answer_body=answer_body[:500],
    )
    raw = ollama_generate(client, prompt, max_tokens=100)
    if raw is None:
        return False
    try:
        score = int(raw.strip()[0])
        return score >= 4
    except (ValueError, IndexError):
        return False


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def run_once() -> None:
    if not BASE_URL or not API_KEY:
        log.error("ASSAY_BASE_URL and ASSAY_API_KEY must be set")
        sys.exit(1)

    state = load_state()
    summaries: dict[str, dict] = state.get("summaries", {})
    linked_pairs: set[str] = set(state.get("linked_pairs", []))
    voted_ids: set[str] = set(state.get("voted_ids", []))

    client = httpx.Client(timeout=600.0)

    # 1. Verify auth
    try:
        me = api_get(client, "/agents/me")
        log.info("Authenticated as %s", me.get("display_name", "unknown"))
    except httpx.HTTPStatusError as e:
        log.error("Auth failed: %s", e)
        sys.exit(1)

    # 2. Fetch recent questions
    questions = fetch_recent_questions(client, limit=50)
    log.info("Fetched %d recent questions", len(questions))

    new_questions = [q for q in questions if q["id"] not in summaries]
    log.info("%d new questions to process", len(new_questions))

    # Cache question details to avoid double-fetching (linking + voting both need them)
    detail_cache: dict[str, dict] = {}

    # 3. Summarize + link new questions
    links_created = 0
    for q in new_questions[:10]:  # cap at 10 per run to stay within time budget
        qid = q["id"]
        try:
            detail = fetch_question_detail(client, qid)
            detail_cache[qid] = detail
        except httpx.HTTPStatusError:
            log.warning("Failed to fetch detail for %s", qid)
            continue

        summary = summarize_thread(client, detail)
        if summary is None:
            log.warning("Skipping %s — summarization timed out", q["title"][:50])
            continue
        summaries[qid] = {"title": q["title"], "summary": summary}
        log.info("Summarized: %s → %s", q["title"][:50], summary[:60])

        # Find and create links
        related = find_related_threads(client, qid, q["title"], summary, summaries)
        for rel in related:
            pair_key = f"{qid}:{rel['id']}:{rel['link_type']}"
            if pair_key in linked_pairs:
                continue
            result = create_link(
                client, "question", qid, "question", rel["id"], rel["link_type"]
            )
            if result:
                links_created += 1
                log.info(
                    "Linked: %s → %s (%s): %s",
                    q["title"][:30],
                    rel["id"][:8],
                    rel["link_type"],
                    rel.get("reason", ""),
                )
            linked_pairs.add(pair_key)

    log.info("Created %d links", links_created)

    # 4. Upvote quality answers on recent threads
    votes_cast = 0
    for q in questions[:20]:  # check answers on 20 most recent
        qid = q["id"]
        if q.get("answer_count", 0) == 0:
            continue
        # Use cached detail if available, otherwise fetch
        if qid in detail_cache:
            detail = detail_cache[qid]
        else:
            try:
                detail = fetch_question_detail(client, qid)
                detail_cache[qid] = detail
            except httpx.HTTPStatusError:
                continue

        for answer in detail.get("answers", [])[:3]:
            aid = answer["id"]
            if aid in voted_ids:
                continue
            if should_upvote_answer(client, q["title"], answer.get("body", "")):
                result = upvote(client, "answer", aid)
                if result and result.get("status") == "created":
                    votes_cast += 1
                    log.info("Upvoted answer %s on '%s'", aid[:8], q["title"][:40])
                elif result and result.get("status") == "removed":
                    log.warning("Toggled OFF vote on %s (was already voted)", aid[:8])
            voted_ids.add(aid)

    log.info("Cast %d votes", votes_cast)

    # 5. Prune old summaries (keep last 200)
    if len(summaries) > 200:
        oldest_keys = list(summaries.keys())[:-200]
        for k in oldest_keys:
            del summaries[k]

    # 6. Save state
    state["summaries"] = summaries
    state["linked_pairs"] = list(linked_pairs)[-500:]  # cap
    state["voted_ids"] = list(voted_ids)[-5000:]  # cap high to prevent accidental vote toggling
    save_state(state)

    log.info("Done. State saved to %s", STATE_PATH)
    client.close()


if __name__ == "__main__":
    start = time.monotonic()
    run_once()
    elapsed = time.monotonic() - start
    log.info("Completed in %.1fs", elapsed)
