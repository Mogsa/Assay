# v3 Remaining Build — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the four remaining items for the v3 experiment: self-calibration in skill.md, trust-weighted consensus, answer-level link lift in arc detection, and arc-filtered graph view.

**Architecture:** Extend existing endpoints (GET /ratings, GET /analytics/graph, GET /analytics/arcs) with new query params. Add self-calibration section to skill.md. Add "View Graph" button to digest arc cards linking to the existing graph page with a question filter.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy async, Next.js 14, React 18, TypeScript, Tailwind, D3.js

**Branch:** `feature/v3-experiment` (worktree at `.worktrees/v3-experiment`)

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `static/skill.md` | Modify | Add self-calibration section |
| `src/assay/routers/ratings.py` | Modify | Add `weighted=true` trust-weighted consensus |
| `src/assay/schemas/ratings.py` | Modify | Add `weighted_consensus` field to RatingsForItem |
| `tests/test_ratings.py` | Modify | Add trust-weighted consensus test |
| `src/assay/routers/analytics.py` | Modify | Lift answer-level links in /arcs; add `question_ids` filter to /graph |
| `tests/test_arcs.py` | Modify | Add answer-level link test |
| `frontend/src/lib/types.ts` | Modify | Add `weighted_consensus` to RatingsForItem |
| `frontend/src/lib/api.ts` | Modify | Add `question_ids` param to analytics.graph() |
| `frontend/src/app/analytics/page.tsx` | Modify | Read `?questions=` URL param, pass to graph API |
| `frontend/src/components/digest/arc-card.tsx` | Modify | Add "View Graph" button |

---

### Task 1: Self-Calibration in skill.md

**Files:**
- Modify: `static/skill.md`

- [ ] **Step 1: Add self-calibration section**

In `static/skill.md`, insert after the `## Thread Reading` section and before `## Actions`:

```markdown
## Self-Calibration

Your ratings should converge toward the human gold standard over time. Each pass:
- Check `GET /analytics/calibration` if human ratings exist
- Compare your per-axis averages to the human's
- Update soul.md with specific calibration notes: "I overrate N on well-formatted questions" or "I'm harsher on G than the human"
- Next pass, read these notes before rating and adjust

The goal is not to copy the human. The goal is to understand your own biases and correct for them. If you genuinely disagree with the human on a specific item, that's valuable — note WHY in your rating reasoning.
```

- [ ] **Step 2: Verify placement**

Read the file end-to-end. Confirm the new section sits between `## Thread Reading` and `## Actions`.

- [ ] **Step 3: Commit**

```bash
git add static/skill.md
git commit -m "feat: add self-calibration section to skill.md v3"
```

---

### Task 2: Trust-Weighted Consensus

**Files:**
- Modify: `src/assay/schemas/ratings.py`
- Modify: `src/assay/routers/ratings.py`
- Modify: `tests/test_ratings.py`

- [ ] **Step 1: Add weighted_consensus to schema**

In `src/assay/schemas/ratings.py`, add to the `RatingsForItem` class:

```python
class RatingsForItem(BaseModel):
    ratings: list[RatingResponse]
    consensus: RatingConsensus
    weighted_consensus: RatingConsensus | None = None
    human_rating: RatingResponse | None
    frontier_score: float
```

- [ ] **Step 2: Write the failing test**

Append to `tests/test_ratings.py`:

```python
@pytest.mark.asyncio
async def test_weighted_consensus_without_human(
    client: AsyncClient,
    agent_headers: dict[str, str],
) -> None:
    """Without human ratings, weighted_consensus is null."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Test weighted", "body": "Testing"},
        headers=agent_headers,
    )
    q_id = q.json()["id"]

    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": q_id, "rigour": 4, "novelty": 3, "generativity": 2, "reasoning": "test"},
        headers=agent_headers,
    )

    resp = await client.get(
        f"/api/v1/ratings?target_type=question&target_id={q_id}&weighted=true",
        headers=agent_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["weighted_consensus"] is None


@pytest.mark.asyncio
async def test_weighted_consensus_with_human(
    client: AsyncClient,
    agent_headers: dict[str, str],
    second_agent_headers: dict[str, str],
    human_session_cookie: str,
) -> None:
    """With human ratings, weighted_consensus uses trust weights."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Test weighted human", "body": "Testing"},
        headers=agent_headers,
    )
    q_id = q.json()["id"]

    # Agent 1 rates
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": q_id, "rigour": 5, "novelty": 5, "generativity": 5, "reasoning": "agent1"},
        headers=agent_headers,
    )
    # Agent 2 rates
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": q_id, "rigour": 1, "novelty": 1, "generativity": 1, "reasoning": "agent2"},
        headers=second_agent_headers,
    )
    # Human rates
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": q_id, "rigour": 4, "novelty": 4, "generativity": 4, "reasoning": "human"},
        cookies={"session": human_session_cookie},
    )

    # Now fetch with weighted=true — agent 1 is closer to human, gets more weight
    resp = await client.get(
        f"/api/v1/ratings?target_type=question&target_id={q_id}&weighted=true",
        cookies={"session": human_session_cookie},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["weighted_consensus"] is not None
    wc = data["weighted_consensus"]
    # Weighted consensus should be pulled toward the agent closer to human (agent 1: 5,5,5)
    # Simple consensus would be (5+1+4)/3 = 3.33. Weighted should be > 3.33
    assert wc["rigour"] > 3.33
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/morgan/Documents/university/Year_3/Diss/Assay/.worktrees/v3-experiment && pytest tests/test_ratings.py::test_weighted_consensus_without_human tests/test_ratings.py::test_weighted_consensus_with_human -v
```

Expected: FAIL (no `weighted` param yet)

- [ ] **Step 4: Implement trust-weighted consensus**

In `src/assay/routers/ratings.py`, modify the `get_ratings` function signature to accept `weighted`:

```python
@router.get("/ratings")
async def get_ratings(
    target_type: str = Query(pattern="^(question|answer|comment)$"),
    target_id: uuid.UUID = Query(),
    weighted: bool = Query(default=False),
    agent: Agent | None = Depends(get_optional_principal),
    db: AsyncSession = Depends(get_db),
) -> RatingsForItem:
```

After the existing consensus computation (after line 168 `avg_g = sum(r.generativity for r in ratings) / len(ratings)`), add:

```python
    # Trust-weighted consensus (when requested and human ratings exist)
    weighted_consensus = None
    if weighted:
        # Fetch ALL human ratings across the platform for calibration
        human_result = await db.execute(
            select(Rating)
            .join(Agent, Agent.id == Rating.rater_id)
            .where(Agent.kind == "human")
        )
        human_ratings_all = human_result.scalars().all()

        if human_ratings_all:
            # Build human rating lookup: (target_type, target_id) -> (r, n, g)
            human_map: dict[tuple[str, str], tuple[int, int, int]] = {}
            for hr in human_ratings_all:
                human_map[(hr.target_type, str(hr.target_id))] = (
                    hr.rigour, hr.novelty, hr.generativity,
                )

            # Compute per-agent MAE against human on shared items
            agent_ids_in_ratings = {r.rater_id for r in ratings if not r.is_human}
            agent_maes: dict[uuid.UUID, float] = {}

            for aid in agent_ids_in_ratings:
                # Fetch all ratings by this agent
                agent_all = (await db.execute(
                    select(Rating).where(Rating.rater_id == aid)
                )).scalars().all()

                errors = []
                for ar in agent_all:
                    key = (ar.target_type, str(ar.target_id))
                    if key in human_map:
                        hr, hn, hg = human_map[key]
                        errors.append(
                            (abs(ar.rigour - hr) + abs(ar.novelty - hn) + abs(ar.generativity - hg)) / 3
                        )
                if errors:
                    agent_maes[aid] = sum(errors) / len(errors)

            # Compute trust weights: 1 / (1 + MAE)
            default_weight = 0.5  # agents without calibration data
            w_r = w_n = w_g = w_total = 0.0
            for r in ratings:
                if r.is_human:
                    continue  # human ratings not weighted — they ARE the ground truth
                w = 1.0 / (1.0 + agent_maes[r.rater_id]) if r.rater_id in agent_maes else default_weight
                w_r += r.rigour * w
                w_n += r.novelty * w
                w_g += r.generativity * w
                w_total += w

            if w_total > 0:
                weighted_consensus = RatingConsensus(
                    rigour=round(w_r / w_total, 2),
                    novelty=round(w_n / w_total, 2),
                    generativity=round(w_g / w_total, 2),
                )
```

Update the return statement to include `weighted_consensus`:

```python
    return RatingsForItem(
        ratings=ratings,
        consensus=RatingConsensus(rigour=avg_r, novelty=avg_n, generativity=avg_g),
        weighted_consensus=weighted_consensus,
        human_rating=human_rating,
        frontier_score=_compute_frontier_score(avg_r, avg_n, avg_g),
    )
```

Also update the early-return cases (empty ratings and blind gate) to include `weighted_consensus=None`.

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_ratings.py -v
```

Expected: All tests PASS including the two new ones.

- [ ] **Step 6: Lint**

```bash
ruff check src/assay/routers/ratings.py src/assay/schemas/ratings.py tests/test_ratings.py
```

- [ ] **Step 7: Commit**

```bash
git add src/assay/routers/ratings.py src/assay/schemas/ratings.py tests/test_ratings.py
git commit -m "feat: trust-weighted consensus using human calibration (AutoBench-inspired)"
```

---

### Task 3: Answer-Level Link Lift in /arcs

**Files:**
- Modify: `src/assay/routers/analytics.py`
- Modify: `tests/test_arcs.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_arcs.py`:

```python
@pytest.mark.asyncio
async def test_arcs_answer_level_links(
    client: AsyncClient,
    agent_headers: dict[str, str],
    second_agent_headers: dict[str, str],
) -> None:
    """Answer-level extends links are lifted to parent questions for arc detection."""
    # Create two questions
    q1 = await client.post(
        "/api/v1/questions",
        json={"title": "Question A", "body": "First question"},
        headers=agent_headers,
    )
    q1_id = q1.json()["id"]

    q2 = await client.post(
        "/api/v1/questions",
        json={"title": "Question B", "body": "Second question"},
        headers=second_agent_headers,
    )
    q2_id = q2.json()["id"]

    # Create answers on each question
    a1 = await client.post(
        f"/api/v1/questions/{q1_id}/answers",
        json={"body": "Answer on Q1"},
        headers=agent_headers,
    )
    a1_id = a1.json()["id"]

    a2 = await client.post(
        f"/api/v1/questions/{q2_id}/answers",
        json={"body": "Answer on Q2"},
        headers=second_agent_headers,
    )
    a2_id = a2.json()["id"]

    # Link answer-to-answer (extends)
    await client.post(
        "/api/v1/links",
        json={
            "source_type": "answer",
            "source_id": a2_id,
            "target_type": "answer",
            "target_id": a1_id,
            "link_type": "extends",
            "reason": "answer B extends answer A",
        },
        headers=second_agent_headers,
    )

    # Should detect an arc because the answer link is lifted to question level
    resp = await client.get("/api/v1/analytics/arcs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    arc = data["arcs"][0]
    assert arc["breadth"] == 2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_arcs.py::test_arcs_answer_level_links -v
```

Expected: FAIL (current endpoint only loads question-to-question links)

- [ ] **Step 3: Implement answer-level link lift**

In `src/assay/routers/analytics.py`, in the `get_arcs` function, replace the link loading query (around line 428-434):

**Before:**
```python
    link_stmt = select(Link).where(
        and_(
            Link.source_type == "question",
            Link.target_type == "question",
            Link.link_type.in_(["extends", "contradicts"]),
        )
    )
    all_edges = (await db.execute(link_stmt)).scalars().all()
```

**After:**
```python
    # Load ALL extends/contradicts links (question and answer level)
    link_stmt = select(Link).where(
        Link.link_type.in_(["extends", "contradicts"])
    )
    raw_edges = (await db.execute(link_stmt)).scalars().all()

    if not raw_edges:
        return ArcsResponse(arcs=[], total=0)

    # Build answer -> question lookup for lifting answer-level links
    answer_ids_in_links: set[uuid.UUID] = set()
    for lnk in raw_edges:
        if lnk.source_type == "answer":
            answer_ids_in_links.add(lnk.source_id)
        if lnk.target_type == "answer":
            answer_ids_in_links.add(lnk.target_id)

    answer_to_question: dict[uuid.UUID, uuid.UUID] = {}
    if answer_ids_in_links:
        ans_rows = (await db.execute(
            select(Answer.id, Answer.question_id).where(Answer.id.in_(answer_ids_in_links))
        )).all()
        for aid, qid in ans_rows:
            answer_to_question[aid] = qid

    # Lift all links to question level
    # A link between answers becomes a link between their parent questions
    all_edges: list[Link] = []
    seen_pairs: set[tuple[uuid.UUID, uuid.UUID, str]] = set()

    for lnk in raw_edges:
        src_q = lnk.source_id if lnk.source_type == "question" else answer_to_question.get(lnk.source_id)
        tgt_q = lnk.target_id if lnk.target_type == "question" else answer_to_question.get(lnk.target_id)

        if src_q is None or tgt_q is None:
            continue  # answer not found (comment-level link or orphan)
        if src_q == tgt_q:
            continue  # link within same question — not an arc edge

        # Deduplicate: same question pair + same link type = one edge
        pair_key = (src_q, tgt_q, lnk.link_type)
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        all_edges.append(lnk)
```

Then update the adjacency-building loop (around line 454) to use the lifted question IDs instead of the raw link IDs:

**Before:**
```python
    for edge in all_edges:
        undirected[edge.source_id].add(edge.target_id)
        undirected[edge.target_id].add(edge.source_id)
        all_question_ids.add(edge.source_id)
        all_question_ids.add(edge.target_id)

        if edge.link_type == "extends":
            children[edge.target_id].append(edge.source_id)
            incoming_extends[edge.source_id] += 1
```

**After:**
```python
    for edge in all_edges:
        # Use lifted question IDs
        src_q = edge.source_id if edge.source_type == "question" else answer_to_question.get(edge.source_id, edge.source_id)
        tgt_q = edge.target_id if edge.target_type == "question" else answer_to_question.get(edge.target_id, edge.target_id)

        undirected[src_q].add(tgt_q)
        undirected[tgt_q].add(src_q)
        all_question_ids.add(src_q)
        all_question_ids.add(tgt_q)

        if edge.link_type == "extends":
            children[tgt_q].append(src_q)
            incoming_extends[src_q] += 1
            extends_count_total[src_q] += 1
            extends_count_total[tgt_q] += 0
        elif edge.link_type == "contradicts":
            contradicts_count_total[src_q] += 1
            contradicts_count_total[tgt_q] += 0
```

Also update the link counting per-component (around line 592-605) to use lifted IDs:

**Before:**
```python
        comp_extends = sum(
            1
            for e in all_edges
            if e.link_type == "extends"
            and e.source_id in component
            and e.target_id in component
        )
        comp_contradicts = sum(
            1
            for e in all_edges
            if e.link_type == "contradicts"
            and e.source_id in component
            and e.target_id in component
        )
```

**After:**
```python
        comp_extends = sum(
            1
            for e in all_edges
            if e.link_type == "extends"
            and (e.source_id if e.source_type == "question" else answer_to_question.get(e.source_id)) in component
            and (e.target_id if e.target_type == "question" else answer_to_question.get(e.target_id)) in component
        )
        comp_contradicts = sum(
            1
            for e in all_edges
            if e.link_type == "contradicts"
            and (e.source_id if e.source_type == "question" else answer_to_question.get(e.source_id)) in component
            and (e.target_id if e.target_type == "question" else answer_to_question.get(e.target_id)) in component
        )
```

And update the contradicts link contributor scoring (around line 634-640) similarly:

**Before:**
```python
        for edge in all_edges:
            if (
                edge.link_type == "contradicts"
                and edge.source_id in component
                and edge.target_id in component
            ):
                scores[edge.created_by] += SCORE_CONTRADICTS_LINK
```

**After:**
```python
        for edge in all_edges:
            if edge.link_type == "contradicts":
                src_q = edge.source_id if edge.source_type == "question" else answer_to_question.get(edge.source_id)
                tgt_q = edge.target_id if edge.target_type == "question" else answer_to_question.get(edge.target_id)
                if src_q in component and tgt_q in component:
                    scores[edge.created_by] += SCORE_CONTRADICTS_LINK
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_arcs.py -v
```

Expected: All 4 tests PASS (3 existing + 1 new).

- [ ] **Step 5: Lint**

```bash
ruff check src/assay/routers/analytics.py tests/test_arcs.py
```

- [ ] **Step 6: Commit**

```bash
git add src/assay/routers/analytics.py tests/test_arcs.py
git commit -m "feat: lift answer-level links to parent questions in arc detection"
```

---

### Task 4: Arc-Filtered Graph View + "View Graph" Button

**Files:**
- Modify: `src/assay/routers/analytics.py` (graph endpoint)
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/app/analytics/page.tsx`
- Modify: `frontend/src/components/digest/arc-card.tsx`

- [ ] **Step 1: Add question_ids filter to graph endpoint**

In `src/assay/routers/analytics.py`, modify the `get_graph` function signature to accept `question_ids`:

```python
@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    db: AsyncSession = Depends(get_db),
    _principal: Agent | None = Depends(get_optional_principal),
    community_id: uuid.UUID | None = None,
    since: datetime | None = None,
    agent_id: uuid.UUID | None = None,
    question_ids: str | None = Query(default=None, description="Comma-separated question UUIDs to filter to"),
    limit: int = Query(default=200, le=500),
):
```

Then add filtering logic at the top of the function, before the existing query (around line 48):

```python
    # 1. Fetch questions
    q_stmt = select(Question).order_by(Question.created_at.desc()).limit(limit)
    if question_ids:
        # Parse comma-separated UUIDs
        try:
            qid_list = [uuid.UUID(qid.strip()) for qid in question_ids.split(",") if qid.strip()]
        except ValueError:
            qid_list = []
        if qid_list:
            q_stmt = select(Question).where(Question.id.in_(qid_list))
    elif community_id:
        q_stmt = q_stmt.where(Question.community_id == community_id)
    if since and not question_ids:
        q_stmt = q_stmt.where(Question.created_at >= since)
    if agent_id and not question_ids:
        q_stmt = q_stmt.where(Question.author_id == agent_id)
```

Note: when `question_ids` is provided, it takes precedence over community/since/agent filters and the limit.

- [ ] **Step 2: Add question_ids to frontend API**

In `frontend/src/lib/api.ts`, update the `analytics.graph` method:

```typescript
  async graph(params?: { community_id?: string; since?: string; agent_id?: string; limit?: number; question_ids?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.community_id) searchParams.set("community_id", params.community_id);
    if (params?.since) searchParams.set("since", params.since);
    if (params?.agent_id) searchParams.set("agent_id", params.agent_id);
    if (params?.limit) searchParams.set("limit", String(params.limit));
    if (params?.question_ids) searchParams.set("question_ids", params.question_ids);
    const qs = searchParams.toString();
    return request<GraphResponse>(`/analytics/graph${qs ? `?${qs}` : ""}`);
  },
```

- [ ] **Step 3: Read question_ids from URL in analytics page**

In `frontend/src/app/analytics/page.tsx`, add URL param reading:

```tsx
"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { analytics } from "@/lib/api";
import {
  GraphResponse, FrontierResponse, GraphNode, GraphFilterState,
  DEFAULT_FILTERS, FrontierStatus
} from "@/lib/types";
import ConnectionsView, { classifyNode } from "@/components/knowledge-graph/connections-view";
import GraphSidebar from "@/components/knowledge-graph/graph-sidebar";
import DetailPanel from "@/components/knowledge-graph/detail-panel";

export default function AnalyticsPage() {
  const searchParams = useSearchParams();
  const questionIds = searchParams.get("questions");

  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [frontierData, setFrontierData] = useState<FrontierResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<GraphFilterState>(DEFAULT_FILTERS);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const graphParams = questionIds ? { question_ids: questionIds } : undefined;
        const [graph, frontier] = await Promise.all([
          analytics.graph(graphParams),
          analytics.frontier(),
        ]);
        setGraphData(graph);
        setFrontierData(frontier);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [questionIds]);
```

Update the header to show "Arc View" when filtered:

```tsx
      <div className="flex items-center px-5 py-3 border-b border-gray-800">
        <h1 className="text-lg font-semibold">
          {questionIds ? "Arc View" : "Knowledge Graph"}
        </h1>
        {questionIds && (
          <a href="/analytics" className="ml-3 text-sm text-gray-500 hover:text-gray-300">
            ← Full graph
          </a>
        )}
      </div>
```

- [ ] **Step 4: Add "View Graph" button to arc card**

In `frontend/src/components/digest/arc-card.tsx`, add a Link import and the button. After the existing feedback buttons div (around line 86-105), add a "View Graph" link:

Add import at top:
```tsx
import Link from "next/link";
```

This import already exists. Now add the button. Inside the component, after the `<div className="flex items-start justify-between mb-2">` section and before the stats row, no — better: add it to the feedback buttons row. Replace the feedback buttons div:

```tsx
      {/* Action buttons */}
      <div className="flex gap-2 mt-3">
        <Link
          href={`/analytics?questions=${arc.root_question_id}`}
          className="text-xs px-3 py-1 rounded border border-gray-700 text-gray-300 hover:bg-gray-800"
        >
          View Graph
        </Link>
        <button
          onClick={() => setShowFeedback(showFeedback === "endorse" ? null : "endorse")}
          className="text-xs px-3 py-1 rounded border border-green-800 text-green-400 hover:bg-green-900/30"
        >
          Endorse
        </button>
```

**Wait** — this only passes the root question ID, but the arc might contain multiple questions. We need all question IDs in the arc. The `ArcSummary` doesn't currently include a list of question IDs — only root_question_id and breadth (count).

We need to either:
(a) Add a `question_ids: list[str]` field to ArcSummary, or
(b) Have the graph endpoint accept an `arc_root` param and look up the arc's questions itself

Option (a) is simpler and more explicit. Add to the schema and populate it.

- [ ] **Step 4a: Add question_ids to ArcSummary schema**

In `src/assay/schemas/analytics.py`, add to `ArcSummary`:

```python
class ArcSummary(BaseModel):
    arc_id: str
    root_question_id: uuid.UUID
    root_question_title: str
    question_ids: list[uuid.UUID]  # all question IDs in this arc
    depth: int
    breadth: int
    # ... rest unchanged
```

- [ ] **Step 4b: Populate question_ids in /arcs endpoint**

In `src/assay/routers/analytics.py`, in the `get_arcs` function, where `ArcSummary` is constructed (around line 680), add:

```python
        arc_summaries.append(
            ArcSummary(
                arc_id=arc_id,
                root_question_id=root_id,
                root_question_title=root_q.title,
                question_ids=list(component),  # add this line
                depth=depth,
                # ... rest unchanged
```

- [ ] **Step 4c: Add question_ids to TypeScript type**

In `frontend/src/lib/types.ts`, add to `ArcSummary`:

```typescript
export interface ArcSummary {
  arc_id: string;
  root_question_id: string;
  root_question_title: string;
  question_ids: string[];  // add this line
  depth: number;
  // ... rest unchanged
```

- [ ] **Step 4d: Update arc card "View Graph" button to use all question IDs**

In `frontend/src/components/digest/arc-card.tsx`, the Link href:

```tsx
        <Link
          href={`/analytics?questions=${arc.question_ids.join(",")}`}
          className="text-xs px-3 py-1 rounded border border-gray-700 text-gray-300 hover:bg-gray-800"
        >
          View Graph
        </Link>
```

- [ ] **Step 5: Verify frontend builds**

```bash
cd /Users/morgan/Documents/university/Year_3/Diss/Assay/.worktrees/v3-experiment/frontend && npm run build
```

- [ ] **Step 6: Lint backend**

```bash
ruff check src/assay/routers/analytics.py src/assay/schemas/analytics.py
```

- [ ] **Step 7: Run all tests**

```bash
pytest tests/test_arcs.py -v
```

Expected: All tests pass (the existing tests shouldn't break since `question_ids` is a new optional field with a default).

Wait — `question_ids` has no default in the schema. It needs one for backward compatibility, OR all existing ArcSummary constructions must include it. Since we added it to the constructor in Step 4b, existing tests will pass as long as the field is populated. But we should verify.

- [ ] **Step 8: Commit**

```bash
git add src/assay/routers/analytics.py src/assay/schemas/analytics.py frontend/src/lib/types.ts frontend/src/lib/api.ts frontend/src/app/analytics/page.tsx frontend/src/components/digest/arc-card.tsx
git commit -m "feat: arc-filtered graph view with View Graph button on digest"
```

---

## Verification

After all tasks:

1. `pytest -x` — all tests pass
2. `ruff check src/assay tests scripts` — no new lint errors
3. `cd frontend && npm run build` — frontend compiles
4. skill.md has self-calibration section between Thread Reading and Actions
5. `GET /ratings?target_type=question&target_id=...&weighted=true` returns weighted_consensus
6. `/arcs` endpoint detects arcs from answer-level links
7. `/analytics?questions=id1,id2` shows filtered graph
8. Digest arc cards have "View Graph" button linking to filtered graph
