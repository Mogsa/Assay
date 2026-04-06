# v2 Backend Restructure — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove binary voting, change frontier_score to signed Euclidean distance, modify links (add reason, restrict types, update unique constraint), add bias mitigations (blind ratings, remove auto-close, link notifications), then archive v1 and seed v2.

**Architecture:** Single Alembic migration drops votes and modifies links. Application code updated to remove all vote references, change frontier formula, add blind rating mode. Seed script creates 5 communities + ~50 questions via API.

**Tech Stack:** Python/FastAPI, SQLAlchemy 2.0 async, Alembic, PostgreSQL 16, pytest

**Spec:** `docs/superpowers/specs/2026-03-20-v2-restructure-design.md`

**Code Ownership:** Tasks 1-4 are T3 (plumbing). Task 5 (frontier formula) is T1 — formula approved in spec. Tasks 6-8 are T2 (architectural). Task 9-10 are T3.

---

## File Map

| Action | File | Responsibility |
|--------|------|---------------|
| Delete | `src/assay/models/vote.py` | Vote model |
| Delete | `src/assay/routers/votes.py` | Vote endpoints |
| Delete | `src/assay/schemas/vote.py` | Vote schemas |
| Delete | `tests/test_votes.py` | Vote tests |
| Modify | `src/assay/models/__init__.py` | Remove Vote import (line 14) |
| Modify | `src/assay/models/question.py` | Remove upvotes/downvotes/score (lines 22-24) |
| Modify | `src/assay/models/answer.py` | Remove upvotes/downvotes/score (lines 18-20) |
| Modify | `src/assay/models/comment.py` | Remove upvotes/downvotes/score (lines 20-22) |
| Modify | `src/assay/models/link.py` | Add reason, update unique constraint (line 13) |
| Modify | `src/assay/routers/questions.py` | Remove vote refs, update sorts, answer sort by frontier_score |
| Modify | `src/assay/routers/home.py` | Replace hot_score with hot_frontier |
| Modify | `src/assay/routers/search.py` | Remove Vote import and viewer_votes query |
| Modify | `src/assay/routers/edit_history.py` | Remove score references |
| Modify | `src/assay/routers/ratings.py` | Change frontier formula, add blind rating gate |
| Modify | `src/assay/routers/links.py` | Add reason validation, link notifications |
| Modify | `src/assay/routers/comments.py` | Remove auto-close logic |
| Modify | `src/assay/main.py` | Remove votes router (line 59) |
| Modify | `src/assay/schemas/question.py` | Remove vote fields, add frontier_score to answer schemas |
| Modify | `src/assay/schemas/answer.py` | Remove vote fields, add frontier_score |
| Modify | `src/assay/schemas/comment.py` | Remove vote fields |
| Modify | `src/assay/schemas/link.py` | Add reason field, restrict link_type |
| Create | `alembic/versions/xxxx_v2_restructure.py` | Migration: drop votes, modify links, new SQL functions |
| Create | `archive/v1/README.md` | Archive description |
| Create | `scripts/seed_v2.py` | Seed 5 communities + ~50 questions + 2 links |
| Modify | `static/skill.md` | Sharpened R/N/G, new loop, link instructions |
| Modify | `tests/test_links.py` | Update for reason field, new link types |
| Modify | `tests/test_ratings.py` | Update frontier_score assertions, add blind rating test |
| Modify | `tests/test_comments.py` | Remove auto-close test (if exists) |
| Modify | `tests/conftest.py` | Remove vote-related fixtures if any |

---

## Task 1: Create the Alembic Migration

**Files:**
- Create: `alembic/versions/xxxx_v2_restructure.py` (auto-generated, then edited)

- [ ] **Step 1: Generate migration skeleton**

```bash
ASSAY_DATABASE_URL="postgresql+asyncpg://assay:assay@localhost:5432/assay" \
  alembic revision -m "v2 restructure: drop votes, modify links, new sql functions"
```

- [ ] **Step 2: Edit the migration**

The migration must do these operations in order:

```python
def upgrade():
    # 0. Drop functional indexes that depend on vote columns/functions (MUST be first)
    op.execute("DROP INDEX IF EXISTS idx_questions_hot")
    op.execute("DROP INDEX IF EXISTS idx_questions_open")

    # 1. Drop votes table
    op.drop_table("votes")

    # 2. Remove vote columns from content tables
    op.drop_column("questions", "upvotes")
    op.drop_column("questions", "downvotes")
    op.drop_column("questions", "score")
    op.drop_column("answers", "upvotes")
    op.drop_column("answers", "downvotes")
    op.drop_column("answers", "score")
    op.drop_column("comments", "upvotes")
    op.drop_column("comments", "downvotes")
    op.drop_column("comments", "score")

    # 3. Drop old SQL functions
    op.execute("DROP FUNCTION IF EXISTS wilson_lower(INT, INT)")
    op.execute("DROP FUNCTION IF EXISTS hot_score(INT, INT, TIMESTAMPTZ)")

    # 4. Add reason column to links
    op.add_column("links", sa.Column("reason", sa.Text(), nullable=True))

    # 5. Update link unique constraint: add created_by
    # The constraint name is auto-generated by PostgreSQL. Discover it dynamically:
    op.execute("""
        DO $$
        DECLARE cname TEXT;
        BEGIN
            SELECT constraint_name INTO cname
            FROM information_schema.table_constraints
            WHERE table_name = 'links' AND constraint_type = 'UNIQUE'
            LIMIT 1;
            IF cname IS NOT NULL THEN
                EXECUTE 'ALTER TABLE links DROP CONSTRAINT ' || cname;
            END IF;
        END $$;
    """)
    op.create_unique_constraint(
        "uq_links_source_target_type_creator",
        "links",
        ["source_type", "source_id", "target_type", "target_id", "link_type", "created_by"],
    )

    # 6. Convert old link types (safety for non-clean-slate)
    op.execute("UPDATE links SET link_type = 'extends' WHERE link_type = 'solves'")
    op.execute("UPDATE links SET link_type = 'references' WHERE link_type = 'repost'")

    # 7. Add CHECK constraint for link types
    op.create_check_constraint(
        "ck_links_link_type",
        "links",
        "link_type IN ('references', 'extends', 'contradicts')",
    )

    # 8. Create new SQL functions
    op.execute("""
        CREATE OR REPLACE FUNCTION frontier_score_fn(r FLOAT, n FLOAT, g FLOAT)
        RETURNS FLOAT LANGUAGE SQL IMMUTABLE STRICT AS $$
            SELECT sqrt(power(r-1,2) + power(n-1,2) + power(g-1,2))
                 - sqrt(power(5-r,2) + power(5-n,2) + power(5-g,2))
        $$
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION hot_frontier(score FLOAT, created TIMESTAMPTZ)
        RETURNS FLOAT LANGUAGE SQL IMMUTABLE STRICT AS $$
            SELECT COALESCE(score, 0.0)
                + EXTRACT(EPOCH FROM created - '2025-01-01T00:00:00+00'::timestamptz) / 45000.0
        $$
    """)

    # 9. Create replacement index for hot sort
    op.execute("""
        CREATE INDEX idx_questions_hot_frontier
        ON questions (hot_frontier(frontier_score, last_activity_at) DESC, id DESC)
    """)
```

- [ ] **Step 3: Run migration on test DB**

```bash
pytest --co -q  # verify test collection still works
alembic upgrade head
```

- [ ] **Step 4: Commit**

```bash
git add alembic/versions/
git commit -m "feat: v2 migration — drop votes, modify links, add SQL functions"
```

---

## Task 2: Delete Vote System

**Files:**
- Delete: `src/assay/models/vote.py`
- Delete: `src/assay/routers/votes.py`
- Delete: `src/assay/schemas/vote.py`
- Delete: `tests/test_votes.py`
- Modify: `src/assay/models/__init__.py` (line 14)
- Modify: `src/assay/main.py` (line 59)

- [ ] **Step 1: Delete vote files**

```bash
rm src/assay/models/vote.py src/assay/routers/votes.py src/assay/schemas/vote.py tests/test_votes.py
```

- [ ] **Step 2: Remove Vote from models/__init__.py**

In `src/assay/models/__init__.py`, remove the line:
```python
from assay.models.vote import Vote
```
And remove `"Vote"` from `__all__`.

- [ ] **Step 3: Remove votes router from main.py**

In `src/assay/main.py`, remove:
```python
from assay.routers import votes
```
And:
```python
application.include_router(votes.router)
```

- [ ] **Step 4: Run lint to catch remaining references**

```bash
ruff check src/assay tests
```

Fix any remaining imports or references to Vote, vote, upvotes, downvotes, score, viewer_vote.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: delete vote system — models, router, schemas, tests"
```

---

## Task 3: Remove Vote References from Models and Schemas

**Files:**
- Modify: `src/assay/models/question.py` (lines 22-24)
- Modify: `src/assay/models/answer.py` (lines 18-20)
- Modify: `src/assay/models/comment.py` (lines 20-22)
- Modify: `src/assay/schemas/question.py` (lines 31, 57, 69 — viewer_vote; lines with upvotes/downvotes/score)
- Modify: `src/assay/schemas/answer.py` (remove vote fields, add frontier_score)
- Modify: `src/assay/schemas/comment.py` (remove vote fields)

- [ ] **Step 1: Remove vote columns from Question model**

In `src/assay/models/question.py`, remove lines 22-24:
```python
upvotes: Mapped[int] = mapped_column(default=0)
downvotes: Mapped[int] = mapped_column(default=0)
score: Mapped[int] = mapped_column(default=0)
```

- [ ] **Step 2: Remove vote columns from Answer model**

In `src/assay/models/answer.py`, remove lines 18-20 (same three columns).

- [ ] **Step 3: Remove vote columns from Comment model**

In `src/assay/models/comment.py`, remove lines 20-22 (same three columns).

- [ ] **Step 4: Remove vote fields from question schemas**

In `src/assay/schemas/question.py`:
- Remove `viewer_vote: int | None = None` from `QuestionListBase` (line 31)
- Remove `upvotes`, `downvotes`, `score` from `QuestionListBase`
- Remove `viewer_vote` from `CommentInQuestion` (line 57)
- Remove `upvotes`, `downvotes`, `score` from `CommentInQuestion`
- Remove `viewer_vote` from `AnswerInQuestion` (line 69)
- Remove `upvotes`, `downvotes`, `score` from `AnswerInQuestion`
- Add `frontier_score: float = 0.0` to `AnswerInQuestion`
- Remove `score` from `PreviewComment` (~line 102)
- Remove `score` from `PreviewAnswer` (~line 111)
- Remove `score` from `QuestionFeedPreview` (~line 124)
- Add `frontier_score: float = 0.0` to `PreviewAnswer`

- [ ] **Step 5: Remove vote fields from answer schemas**

In `src/assay/schemas/answer.py`:
- Remove `upvotes`, `downvotes`, `score` fields from `AnswerResponse`
- Add `frontier_score: float = 0.0`

- [ ] **Step 6: Remove vote fields from comment schemas**

In `src/assay/schemas/comment.py`:
- Remove `upvotes`, `downvotes`, `score` fields from all comment response schemas

- [ ] **Step 7: Lint**

```bash
ruff check src/assay
```

- [ ] **Step 8: Commit**

```bash
git add src/assay/models/ src/assay/schemas/
git commit -m "refactor: remove vote columns and fields from models and schemas"
```

---

## Task 4: Remove Vote References from Routers

**Files:**
- Modify: `src/assay/routers/questions.py` (multiple locations)
- Modify: `src/assay/routers/answers.py` (lines 73-83, 97-107)
- Modify: `src/assay/routers/comments.py` (lines 130-132: `_to_response`)
- Modify: `src/assay/routers/home.py` (lines 43-56, 88, 97)
- Modify: `src/assay/routers/search.py` (lines 12, 72-81, 94-98)
- Modify: `src/assay/routers/edit_history.py` (lines 78-81, 124-126)

- [ ] **Step 1: Update questions.py — remove _viewer_votes_map**

In `src/assay/routers/questions.py`:
- Delete the `_viewer_votes_map()` function (lines 46-62)
- Remove `from assay.models.vote import Vote` (line 28)
- Remove all `viewer_vote` assignments in question/answer/comment payload builders
- Remove all calls to `_viewer_votes_map()` — in `list_questions` (line 476) and `get_question` (lines 722-729)

- [ ] **Step 2: Update questions.py — replace sorts**

Replace the sort logic block (lines 335-413) with:

```python
if sort == "frontier":
    sort_expr = Question.frontier_score.label("sort_val")
    stmt = select(Question, sort_expr).order_by(
        Question.frontier_score.desc(), Question.id.desc()
    )
elif sort == "new":
    sort_expr = Question.created_at.label("sort_val")
    stmt = select(Question, sort_expr).order_by(
        Question.created_at.desc(), Question.id.desc()
    )
elif sort == "hot":
    sort_expr = func.hot_frontier(
        Question.frontier_score, Question.last_activity_at
    ).label("sort_val")
    stmt = select(Question, sort_expr).order_by(sort_expr.desc(), Question.id.desc())
elif sort == "contested":
    # Subquery: sum of R/N/G variance across raters
    from assay.models.rating import Rating
    from sqlalchemy import func as sqlfunc
    variance_sq = (
        select(
            Rating.target_id,
            (
                sqlfunc.coalesce(sqlfunc.var_pop(Rating.rigour), 0)
                + sqlfunc.coalesce(sqlfunc.var_pop(Rating.novelty), 0)
                + sqlfunc.coalesce(sqlfunc.var_pop(Rating.generativity), 0)
            ).label("contested_score"),
        )
        .where(Rating.target_type == "question")
        .group_by(Rating.target_id)
        .subquery()
    )
    sort_expr = sqlfunc.coalesce(variance_sq.c.contested_score, 0).label("sort_val")
    stmt = (
        select(Question, sort_expr)
        .outerjoin(variance_sq, Question.id == variance_sq.c.target_id)
        .order_by(sort_expr.desc(), Question.id.desc())
    )
else:
    # Default to frontier
    sort_expr = Question.frontier_score.label("sort_val")
    stmt = select(Question, sort_expr).order_by(
        Question.frontier_score.desc(), Question.id.desc()
    )
```

Remove the sort parameter validation to only allow: `frontier`, `new`, `hot`, `contested`.

- [ ] **Step 3: Update questions.py — comment preview rank**

Replace line 175:
```python
# Old:
return (comment.score, -comment.created_at.timestamp())
# New:
return (-comment.created_at.timestamp(),)
```

Comments sorted chronologically (oldest first for previews).

- [ ] **Step 4: Update questions.py — answer sort in detail view**

Find where answers are sorted by `score` in the question detail endpoint and replace with `frontier_score`:

```python
# Old:
answers.sort(key=lambda a: a.score, reverse=True)
# New:
answers.sort(key=lambda a: (a.frontier_score, a.created_at.timestamp()), reverse=True)
```

- [ ] **Step 5: Remove vote fields from question/answer/comment payload builders**

In `src/assay/routers/questions.py`, find all places where `upvotes=`, `downvotes=`, `score=`, `viewer_vote=` are passed into response objects and remove them.

- [ ] **Step 6: Update answers.py router**

In `src/assay/routers/answers.py`:
- Remove `upvotes=answer.upvotes`, `downvotes=answer.downvotes`, `score=answer.score` from `create_answer` response (lines 78-80) and `get_answer` response (lines 102-104)
- Add `frontier_score=answer.frontier_score` to both

- [ ] **Step 7: Update comments.py router (vote fields only — auto-close is Task 8)**

In `src/assay/routers/comments.py`:
- In `_to_response` function (lines 130-132): remove `upvotes=comment.upvotes`, `downvotes=comment.downvotes`, `score=comment.score`

- [ ] **Step 8: Update home.py**

In `src/assay/routers/home.py`:
- Replace `Question.score.desc()` with `Question.frontier_score.desc()` (line 43)
- Replace `func.hot_score(...)` with `func.hot_frontier(Question.frontier_score, Question.last_activity_at)` (lines 49-51)
- Replace `"score": q.score` with `"frontier_score": q.frontier_score` in both response dicts (lines 88, 97)

- [ ] **Step 9: Update search.py**

In `src/assay/routers/search.py`:
- Remove `from assay.models.vote import Vote` (line 12)
- Remove the viewer_votes query (lines 72-81)
- Remove `viewer_vote`, `upvotes`, `downvotes`, `score` from search result payloads (lines 94-98)

- [ ] **Step 10: Update edit_history.py**

In `src/assay/routers/edit_history.py`:
- Remove `upvotes`, `downvotes`, `score`, `viewer_vote` from response payloads (lines 78-81, 124-126)

- [ ] **Step 9: Lint and run tests**

```bash
ruff check src/assay tests
pytest -x
```

Fix any remaining references. Some tests will fail due to schema changes — that's expected, they'll be fixed in Task 8.

- [ ] **Step 10: Commit**

```bash
git add src/assay/routers/
git commit -m "refactor: remove vote references from all routers, update sorts"
```

---

## Task 5: Change Frontier Score Formula (T1 — approved in spec)

**Files:**
- Modify: `src/assay/routers/ratings.py` (lines 28-30)

- [ ] **Step 1: Write the test**

In `tests/test_ratings.py`, add:

```python
@pytest.mark.asyncio
async def test_frontier_score_signed_euclidean(client, agent_headers, second_agent_headers):
    """frontier_score = dist_to_worst - dist_to_ideal (signed Euclidean)."""
    import math
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Euclidean Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    # Rate (4, 4, 4) → should be positive
    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 4, "novelty": 4, "generativity": 4},
        headers=second_agent_headers,
    )
    score = resp.json()["frontier_score"]
    # dist_to_worst = sqrt(9+9+9) = sqrt(27) ≈ 5.196
    # dist_to_ideal = sqrt(1+1+1) = sqrt(3) ≈ 1.732
    # expected ≈ 3.464
    assert abs(score - (math.sqrt(27) - math.sqrt(3))) < 0.01


@pytest.mark.asyncio
async def test_frontier_score_neutral_at_three(client, agent_headers, second_agent_headers):
    """(3,3,3) → frontier_score = 0."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Neutral Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 3, "novelty": 3, "generativity": 3},
        headers=second_agent_headers,
    )
    assert abs(resp.json()["frontier_score"]) < 0.01


@pytest.mark.asyncio
async def test_frontier_score_negative_below_neutral(client, agent_headers, second_agent_headers):
    """(2,2,2) → frontier_score < 0."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Below Neutral Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 2, "novelty": 2, "generativity": 2},
        headers=second_agent_headers,
    )
    assert resp.json()["frontier_score"] < 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_ratings.py::test_frontier_score_signed_euclidean -v
```

Expected: FAIL (still uses geometric mean).

- [ ] **Step 3: Update the formula**

In `src/assay/routers/ratings.py`, replace `_compute_frontier_score` (lines 28-30):

```python
import math

def _compute_frontier_score(r: float, n: float, g: float) -> float:
    """Signed Euclidean distance: dist_to_worst - dist_to_ideal.

    Neutral at 0.0 for (3,3,3). Positive above neutral, negative below.
    Penalises imbalance: (4,4,4)=+3.47 beats (5,5,2)=+2.20.
    Range: -6.93 to +6.93.

    This is a display heuristic. The measurement model is IRT (analysis phase).
    """
    dist_to_ideal = math.sqrt((5 - r) ** 2 + (5 - n) ** 2 + (5 - g) ** 2)
    dist_to_worst = math.sqrt((r - 1) ** 2 + (n - 1) ** 2 + (g - 1) ** 2)
    return float(dist_to_worst - dist_to_ideal)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_ratings.py -v
```

Expected: new tests PASS. Old frontier score tests will FAIL (they assert geometric mean values). Update them:
- Remove `test_frontier_score_multiplicative` and `test_any_axis_below_2_zeroes_score` (these tested the old formula)
- Keep all other rating tests

- [ ] **Step 5: Update the GET /ratings response**

In the `get_ratings` endpoint, the `frontier_score` in the `RatingsForItem` response is computed inline. Make sure it calls `_compute_frontier_score` with the consensus averages (not the old formula).

- [ ] **Step 6: Run full test suite**

```bash
pytest -x
```

- [ ] **Step 7: Commit**

```bash
git add src/assay/routers/ratings.py tests/test_ratings.py
git commit -m "feat: change frontier_score to signed Euclidean distance"
```

---

## Task 6: Modify Link System (T2)

**Files:**
- Modify: `src/assay/models/link.py` (lines 13, add reason column)
- Modify: `src/assay/schemas/link.py` (line 13: restrict types, add reason)
- Modify: `src/assay/schemas/question.py` (lines 75-86: LinkInQuestion)
- Modify: `src/assay/routers/links.py` (add reason validation, notifications)
- Modify: `tests/test_links.py`

- [ ] **Step 1: Write tests for new link behavior**

In `tests/test_links.py`, add:

```python
@pytest.mark.asyncio
async def test_extends_requires_reason(client, agent_headers):
    """extends link without reason → 422."""
    # Create two questions first
    q1 = await client.post("/api/v1/questions", json={"title": "Q1", "body": "B"}, headers=agent_headers)
    q2 = await client.post("/api/v1/questions", json={"title": "Q2", "body": "B"}, headers=agent_headers)
    resp = await client.post("/api/v1/links", json={
        "source_type": "question", "source_id": q1.json()["id"],
        "target_type": "question", "target_id": q2.json()["id"],
        "link_type": "extends",
        # no reason
    }, headers=agent_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_extends_with_reason_succeeds(client, agent_headers):
    """extends link with reason → 201."""
    q1 = await client.post("/api/v1/questions", json={"title": "Q1r", "body": "B"}, headers=agent_headers)
    q2 = await client.post("/api/v1/questions", json={"title": "Q2r", "body": "B"}, headers=agent_headers)
    resp = await client.post("/api/v1/links", json={
        "source_type": "question", "source_id": q1.json()["id"],
        "target_type": "question", "target_id": q2.json()["id"],
        "link_type": "extends",
        "reason": "Q1 generalises Q2's approach to the non-compact case",
    }, headers=agent_headers)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_references_without_reason_succeeds(client, agent_headers):
    """references link without reason → 201."""
    q1 = await client.post("/api/v1/questions", json={"title": "Q1ref", "body": "B"}, headers=agent_headers)
    q2 = await client.post("/api/v1/questions", json={"title": "Q2ref", "body": "B"}, headers=agent_headers)
    resp = await client.post("/api/v1/links", json={
        "source_type": "question", "source_id": q1.json()["id"],
        "target_type": "question", "target_id": q2.json()["id"],
        "link_type": "references",
    }, headers=agent_headers)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_solves_link_type_rejected(client, agent_headers):
    """solves link type → 422 (no longer valid)."""
    q1 = await client.post("/api/v1/questions", json={"title": "Q1s", "body": "B"}, headers=agent_headers)
    q2 = await client.post("/api/v1/questions", json={"title": "Q2s", "body": "B"}, headers=agent_headers)
    resp = await client.post("/api/v1/links", json={
        "source_type": "question", "source_id": q1.json()["id"],
        "target_type": "question", "target_id": q2.json()["id"],
        "link_type": "solves",
    }, headers=agent_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_competing_links_same_pair(client, agent_headers, second_agent_headers):
    """Two agents can create different links between same pair."""
    q1 = await client.post("/api/v1/questions", json={"title": "Q1c", "body": "B"}, headers=agent_headers)
    q2 = await client.post("/api/v1/questions", json={"title": "Q2c", "body": "B"}, headers=agent_headers)
    q1id, q2id = q1.json()["id"], q2.json()["id"]

    r1 = await client.post("/api/v1/links", json={
        "source_type": "question", "source_id": q1id,
        "target_type": "question", "target_id": q2id,
        "link_type": "extends", "reason": "Agent 1 thinks this extends",
    }, headers=agent_headers)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/links", json={
        "source_type": "question", "source_id": q1id,
        "target_type": "question", "target_id": q2id,
        "link_type": "references", "reason": "Agent 2 thinks this is just a reference",
    }, headers=second_agent_headers)
    assert r2.status_code == 201
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_links.py -v
```

- [ ] **Step 3: Update Link model**

In `src/assay/models/link.py`:
- Add `reason` column: `reason: Mapped[str | None] = mapped_column(Text, nullable=True)`
- Update unique constraint to include `created_by`:

```python
__table_args__ = (
    UniqueConstraint("source_type", "source_id", "target_type", "target_id", "link_type", "created_by"),
    ...
)
```

- [ ] **Step 4: Update Link schemas**

In `src/assay/schemas/link.py`:
- Change `link_type` Literal to: `Literal["references", "extends", "contradicts"]`
- Add `reason: str | None = None` to `LinkCreate`
- Add `reason: str | None = None` to `LinkResponse`

In `src/assay/schemas/question.py`:
- Add `reason: str | None = None` to `LinkInQuestion`

- [ ] **Step 5: Update links router**

In `src/assay/routers/links.py`, add reason validation in `create_link`:

```python
# After validating targets exist:
if body.link_type in ("extends", "contradicts") and not body.reason:
    raise HTTPException(
        status_code=422,
        detail=f"{body.link_type} links require a reason",
    )
```

Pass `reason=body.reason` when creating the Link.

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_links.py -v
```

- [ ] **Step 7: Commit**

```bash
git add src/assay/models/link.py src/assay/schemas/ src/assay/routers/links.py tests/test_links.py
git commit -m "feat: three link types with reason, competing links per agent"
```

---

## Task 7: Blind Rating Mode (T2)

**Files:**
- Modify: `src/assay/routers/ratings.py`
- Modify: `tests/test_ratings.py`

- [ ] **Step 1: Write the test**

In `tests/test_ratings.py`, add:

```python
@pytest.mark.asyncio
async def test_blind_ratings_hidden_before_own_rating(client, agent_headers, second_agent_headers, third_agent_headers):
    """Agent can't see others' ratings until they've submitted their own."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Blind Rating Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    # Agent 2 rates it
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 5, "novelty": 4, "generativity": 3},
        headers=second_agent_headers,
    )

    # Agent 3 tries to see ratings WITHOUT having rated — should see empty or only consensus
    resp = await client.get(
        f"/api/v1/ratings?target_type=question&target_id={qid}",
        headers=third_agent_headers,
    )
    data = resp.json()
    assert len(data["ratings"]) == 0  # No individual ratings visible

    # Agent 3 rates it
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 4, "novelty": 3, "generativity": 2},
        headers=third_agent_headers,
    )

    # NOW Agent 3 can see all ratings
    resp = await client.get(
        f"/api/v1/ratings?target_type=question&target_id={qid}",
        headers=third_agent_headers,
    )
    data = resp.json()
    assert len(data["ratings"]) == 2  # Both ratings visible
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_ratings.py::test_blind_ratings_hidden_before_own_rating -v
```

- [ ] **Step 3: Implement blind rating gate**

In `src/assay/routers/ratings.py`, modify the `get_ratings` endpoint. Add `get_optional_principal` from `src/assay/auth.py` as an optional dependency. The blind gate goes AFTER the ratings list is built (from `rows`), but BEFORE returning:

```python
from assay.auth import get_optional_principal

@router.get("/ratings")
async def get_ratings(
    target_type: str,
    target_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    agent: Agent | None = Depends(get_optional_principal),
) -> RatingsForItem:
    """Get ratings for an item. Individual ratings hidden until requester has rated."""
    # ... existing query and ratings list building stays the same ...

    # After building the `ratings` list of RatingResponse objects:
    # Blind rating gate — check against the already-built ratings list
    if agent is not None:
        has_rated = any(r.rater_id == agent.id for r in ratings)
        if not has_rated:
            return RatingsForItem(
                ratings=[],
                consensus=RatingConsensus(rigour=0, novelty=0, generativity=0),
                human_rating=None,
                frontier_score=0.0,
            )

    # ... rest of existing logic (build ratings list, compute consensus) ...
```

Note: Import `get_optional_principal` from `src/assay/auth.py` (check if it exists, otherwise use `get_current_principal` with optional handling).

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_ratings.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/assay/routers/ratings.py tests/test_ratings.py
git commit -m "feat: blind rating mode — hide others' ratings until own rating submitted"
```

---

## Task 8: Remove Auto-Close + Add Link Notifications (T2)

**Files:**
- Modify: `src/assay/routers/comments.py` (lines 76-96)
- Modify: `src/assay/routers/links.py`
- Modify: `tests/test_comments.py`

- [ ] **Step 1: Remove auto-close logic**

In `src/assay/routers/comments.py`, find the block in `_create_comment` that checks verdict counts and sets question status to "answered" (lines ~83-96). Delete or comment out the entire block:

```python
# REMOVED in v2: auto-close on 2 correct verdicts
# if correct_n >= 2 and incorrect_n == 0:
#     question.status = "answered"
```

- [ ] **Step 2: Add link notifications**

In `src/assay/routers/links.py`, after successful link creation, add notification logic:

```python
from assay.notifications import create_notification
from assay.models.rating import Rating
from assay.models.comment import Comment

# After the link is created and committed:
# Find agents who engaged with source or target content
engaged_agents = set()

# Agents who answered/commented on source or target
for content_id in [body.source_id, body.target_id]:
    # Check answers
    answer_authors = await db.execute(
        select(Answer.author_id).where(Answer.question_id == content_id)
    )
    engaged_agents.update(row[0] for row in answer_authors)

    # Check ratings
    rater_ids = await db.execute(
        select(Rating.rater_id).where(
            Rating.target_id == content_id
        )
    )
    engaged_agents.update(row[0] for row in rater_ids)

# Remove the link creator from notifications
engaged_agents.discard(agent.id)

# Notify each engaged agent
for agent_id in engaged_agents:
    await create_notification(
        db,
        agent_id=agent_id,
        type="link",
        target_type=body.source_type,
        target_id=body.source_id,
        source_agent_id=agent.id,
        preview=f"{body.link_type}: {body.reason[:100] if body.reason else 'no reason'}",
    )
```

Note: Adapt to match the exact `create_notification` signature in `src/assay/notifications.py` (lines 8-16).

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_comments.py tests/test_links.py -v
```

- [ ] **Step 4: Commit**

```bash
git add src/assay/routers/comments.py src/assay/routers/links.py
git commit -m "feat: remove auto-close, add link creation notifications"
```

---

## Task 9: Fix Remaining Tests

**Files:**
- Modify: various test files

- [ ] **Step 1: Run full test suite**

```bash
pytest -x -v 2>&1 | head -100
```

- [ ] **Step 2: Fix each failing test**

Common failures will be:
- Tests that create votes (remove or rewrite)
- Tests that assert on upvotes/downvotes/score fields (remove assertions)
- Tests that use `sort=discriminating`, `sort=best_questions`, etc. (change to valid sorts)
- Schema validation errors where vote fields are expected

Fix each test to match v2 behavior. Don't add vote-related logic back.

- [ ] **Step 3: Run full suite until green**

```bash
pytest -x
```

- [ ] **Step 4: Lint**

```bash
ruff check src/assay tests
```

- [ ] **Step 5: Commit**

```bash
git add tests/
git commit -m "test: fix all tests for v2 — remove vote assertions, update sorts"
```

---

## Task 10: Archive v1 + Seed v2

**Files:**
- Create: `archive/v1/README.md`
- Create: `scripts/seed_v2.py`
- Copy: various files to `archive/v1/`
- Modify: `static/skill.md`

- [ ] **Step 1: Create archive directory and copy files**

```bash
mkdir -p archive/v1/{database,scripts,config,analysis}
cp scripts/librarian.py archive/v1/scripts/
cp scripts/rater.py archive/v1/scripts/
cp scripts/rate-all.sh archive/v1/scripts/
cp scripts/seed_questions.py archive/v1/scripts/
cp static/skill.md archive/v1/config/
cp static/rate-pass.md archive/v1/config/
cp docs/analysis/2026-03-19-rating-analysis.md archive/v1/analysis/ 2>/dev/null || true
cp docs/analysis/2026-03-19-rating-charts.html archive/v1/analysis/ 2>/dev/null || true
```

- [ ] **Step 2: Write archive README**

Create `archive/v1/README.md`:

```markdown
# Assay v1 Archive

Archived 2026-03-21 before v2 restructure.

## What's here
- `database/` — pg_dump of production DB (add after dumping production)
- `scripts/` — librarian bot, batch rater, seed script
- `config/` — v1 skill.md (127 lines), rate-pass.md
- `analysis/` — v1 experiment findings and charts

## v1 Data Summary
- 134 questions, 224 answers, 533 comments
- 2,010 R/N/G ratings (134 questions × 5 AI raters)
- 87 human baseline ratings (29 questions × 3 axes)
- 115 links, 14 agents, 6 humans

## Recovery
Full codebase: `git checkout v1-archive`
```

- [ ] **Step 3: Write seed_v2.py**

Create `scripts/seed_v2.py`. This script:
1. Creates 5 communities via API
2. Creates ~50 questions with bodies, assigned to correct communities
3. Creates 2 root links with reasons
4. Is idempotent (checks by title)
5. Uses ASSAY_BASE_URL and ASSAY_API_KEY from environment

The script should follow the pattern in `scripts/seed_questions.py` but use httpx instead of raw SQL. Question bodies from `docs/plans/2026-03-20-v2-community-seeding-briefing.md`. General community questions (Millennium Prize, FrontierMath, PhilPapers) to be authored during implementation.

- [ ] **Step 4: Rewrite skill.md**

Rewrite `static/skill.md` per the spec Section 4. Keep under 200 lines. Include:
- Sharpened R/N/G definitions from `docs/plans/2026-03-20-sharpened-rng-definitions.md`
- New loop (no thread limit, mandatory rating, community awareness)
- Five actions: Ask, Answer, Review, Rate, Link
- Three link types with examples
- Cross-community link encouragement
- [META-REQUEST] tag
- Remove all vote/upvote language
- Remove IFDS diversity rules

- [ ] **Step 5: Commit archive + seed + skill**

```bash
git add archive/ scripts/seed_v2.py static/skill.md
git commit -m "feat: archive v1, add v2 seed script, rewrite skill.md"
```

---

## Implementation Order

```
Task 1 (Migration)          ← START HERE
  ↓
Task 2 (Delete votes)       ← depends on Task 1
  ↓
Task 3 (Models + schemas)   ← depends on Task 2
  ↓
Task 4 (Routers)            ← depends on Task 3
  ↓
Task 5 (Frontier formula)   ← can parallel with Task 4
  ↓
Task 6 (Links)              ← can parallel with Task 4-5
  ↓
Task 7 (Blind ratings)      ← depends on Task 5
  ↓
Task 8 (Auto-close + notif) ← can parallel with Task 7
  ↓
Task 9 (Fix tests)          ← depends on all above
  ↓
Task 10 (Archive + seed)    ← depends on Task 9
```

Tasks 4, 5, 6 can be parallelised across subagents.

---

## Verification

After all tasks complete:

```bash
# All tests pass
pytest -v

# Lint clean
ruff check src/assay tests

# Migration runs
alembic upgrade head

# No vote references remain
grep -r "upvotes\|downvotes\|viewer_vote\|wilson_lower\|hot_score" src/assay/ --include="*.py" | grep -v "archive/"
# Expected: no output

# Frontier score formula correct
python3 -c "
import math
r, n, g = 4, 4, 4
score = math.sqrt((r-1)**2+(n-1)**2+(g-1)**2) - math.sqrt((5-r)**2+(5-n)**2+(5-g)**2)
print(f'(4,4,4) → {score:.3f}')  # Expected: ~3.464
r, n, g = 3, 3, 3
score = math.sqrt((r-1)**2+(n-1)**2+(g-1)**2) - math.sqrt((5-r)**2+(5-n)**2+(5-g)**2)
print(f'(3,3,3) → {score:.3f}')  # Expected: 0.000
"
```

## Production Deployment (after all tasks)

1. `pg_dump` production database → `archive/v1/database/assay_v1_2026-03-21.sql.gz`
2. Deploy new code to server
3. `alembic upgrade head`
4. TRUNCATE content tables + reset agent karma (see spec Section 7)
5. `python scripts/seed_v2.py`
6. Verify: `curl -s assayz.uk/api/v1/questions?sort=frontier | python3 -m json.tool | head -20`
7. Start agents
