# Knowledge Graph UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the analytics knowledge graph into a two-level zoom (overview → community drill-down) with status-colored question nodes, semantic-only edges, functional sidebar filters, and hover tooltips.

**Architecture:** Single D3 force-directed graph replaces two tabs (Connections + Frontier Map). Overview shows questions-only grouped by community gravity wells with semantic edges. Clicking a community zooms into a drill-down showing answers, reviews, agent dots, and structural edges. Sidebar filters control visibility of statuses and link types.

**Tech Stack:** Next.js 14, React 18, TypeScript, D3.js, Tailwind CSS (frontend); FastAPI, SQLAlchemy, Pydantic (backend — minor changes)

**Spec:** `docs/superpowers/specs/2026-03-15-knowledge-graph-ux-redesign-design.md`

**Branch:** `knowledge-graph` worktree at `.worktrees/knowledge-graph/`

---

## Chunk 1: Backend + Types

### Task 1: Add community_id and community metadata to graph API

The graph endpoint returns nodes but doesn't include `community_id` or community names. Both are needed for grouping and labeling.

**Files:**
- Modify: `.worktrees/knowledge-graph/src/assay/schemas/analytics.py:13` (GraphNode), `:46` (GraphResponse)
- Modify: `.worktrees/knowledge-graph/src/assay/routers/analytics.py:34-179` (get_graph)
- Modify: `.worktrees/knowledge-graph/tests/test_analytics.py`

- [ ] **Step 1: Write failing test — graph nodes include community_id**

Add to `tests/test_analytics.py` after `test_graph_includes_comments`:

```python
@pytest.mark.anyio
async def test_graph_includes_community_data(client: AsyncClient, agent_headers: dict):
    """Graph returns community_id on nodes and communities list."""
    # Create a community
    community = await client.post("/api/v1/communities", json={
        "name": "test-math", "display_name": "Mathematics", "description": "Math topics"
    }, headers=agent_headers)
    assert community.status_code == 201
    community_id = community.json()["id"]

    # Create question in that community
    q = await client.post("/api/v1/questions", json={
        "title": "Graph theory Q", "body": "body", "community_id": community_id
    }, headers=agent_headers)
    assert q.status_code == 201

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    data = resp.json()

    q_node = next(n for n in data["nodes"] if n["type"] == "question")
    assert q_node["community_id"] == community_id

    # Communities list present
    assert "communities" in data
    assert len(data["communities"]) >= 1
    comm = next(c for c in data["communities"] if c["id"] == community_id)
    assert comm["name"] == "Mathematics"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .worktrees/knowledge-graph && pytest tests/test_analytics.py::test_graph_includes_community_data -v`
Expected: FAIL — `community_id` not in GraphNode, `communities` not in response

- [ ] **Step 3: Add community_id to GraphNode schema**

In `src/assay/schemas/analytics.py`, add to `GraphNode` class after line 28 (`created_at`):

```python
    community_id: uuid.UUID | None = None  # questions only; null for answers/comments
```

- [ ] **Step 4: Add GraphCommunity schema and update GraphResponse**

In `src/assay/schemas/analytics.py`, add after `GraphAgent` class (line 44):

```python
class GraphCommunity(BaseModel):
    id: uuid.UUID
    name: str
```

Update `GraphResponse` to:

```python
class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    agents: list[GraphAgent]
    communities: list[GraphCommunity] = []
```

- [ ] **Step 5: Populate community_id in graph router**

In `src/assay/routers/analytics.py`, update the question node creation (around line 111) to include `community_id=q.community_id`.

After the agents list build (line 177), add community fetching:

```python
    # 9. Build communities list
    from assay.models.community import Community as CommunityModel
    community_ids = {q.community_id for q in questions if q.community_id}
    graph_communities = []
    if community_ids:
        communities = (await db.execute(
            select(CommunityModel).where(CommunityModel.id.in_(community_ids))
        )).scalars().all()
        graph_communities = [
            GraphCommunity(id=c.id, name=c.display_name)
            for c in communities
        ]
```

Update the import at top to include `GraphCommunity`. Update the return to include `communities=graph_communities`.

- [ ] **Step 6: Run test to verify it passes**

Run: `cd .worktrees/knowledge-graph && pytest tests/test_analytics.py -v`
Expected: ALL pass including the new test

- [ ] **Step 7: Commit**

```bash
cd .worktrees/knowledge-graph
git add src/assay/schemas/analytics.py src/assay/routers/analytics.py tests/test_analytics.py
git commit -m "feat: add community_id and communities to graph API"
```

### Task 2: Update frontend types and API client

**Files:**
- Modify: `.worktrees/knowledge-graph/frontend/src/lib/types.ts:297-334`

- [ ] **Step 1: Add community_id to GraphNode**

In `frontend/src/lib/types.ts`, add to `GraphNode` interface after `created_at`:

```typescript
  community_id: string | null;
```

- [ ] **Step 2: Add GraphCommunity interface**

After `GraphAgent` interface:

```typescript
export interface GraphCommunity {
  id: string;
  name: string;
}
```

- [ ] **Step 3: Update GraphResponse**

```typescript
export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  agents: GraphAgent[];
  communities: GraphCommunity[];
}
```

- [ ] **Step 4: Add GraphFilterState type**

After `FrontierResponse` interface:

```typescript
export type FrontierStatus = "frontier" | "debated" | "resolved" | "explored" | "isolated";

export interface GraphFilterState {
  showFrontier: boolean;
  showDebated: boolean;
  showResolved: boolean;
  showExplored: boolean;
  showIsolated: boolean;
  showExtends: boolean;
  showContradicts: boolean;
  showReferences: boolean;
  showSolves: boolean;
  showRepost: boolean;
  view: "overview" | "community";
  selectedCommunityId: string | null;
  selectedNodeId: string | null;
}

export const DEFAULT_FILTERS: GraphFilterState = {
  showFrontier: true,
  showDebated: true,
  showResolved: true,
  showExplored: true,
  showIsolated: true,
  showExtends: true,
  showContradicts: true,
  showReferences: true,
  showSolves: true,
  showRepost: true,
  view: "overview",
  selectedCommunityId: null,
  selectedNodeId: null,
};
```

- [ ] **Step 5: Commit**

```bash
cd .worktrees/knowledge-graph
git add frontend/src/lib/types.ts
git commit -m "feat: add community and filter types for graph redesign"
```

---

## Chunk 2: Detail Panel Fix + Sidebar Rewrite

### Task 3: Fix detail panel D3 mutation bug

The detail panel compares `e.source === node.id`, but D3 mutates `source`/`target` from strings to objects after simulation runs.

**Files:**
- Modify: `.worktrees/knowledge-graph/frontend/src/components/knowledge-graph/detail-panel.tsx:12-14,74-76`

- [ ] **Step 1: Fix connectedEdges filter (line 12-14)**

Replace:
```typescript
  const connectedEdges = data.edges.filter(
    e => e.source === node.id || e.target === node.id
  );
```

With:
```typescript
  const sourceId = (e: any) => e.source?.id ?? e.source;
  const targetId = (e: any) => e.target?.id ?? e.target;
  const connectedEdges = data.edges.filter(
    e => sourceId(e) === node.id || targetId(e) === node.id
  );
```

- [ ] **Step 2: Fix otherId computation (line 74-76)**

Replace:
```typescript
              const otherId = edge.source === node.id ? edge.target : edge.source;
```

With:
```typescript
              const edgeSrc = (edge as any).source?.id ?? edge.source;
              const edgeTgt = (edge as any).target?.id ?? edge.target;
              const otherId = edgeSrc === node.id ? edgeTgt : edgeSrc;
```

- [ ] **Step 3: Add community label to cross-community connections**

In the connections list JSX (around line 87), update the display to show community name for cross-community links:

```typescript
                  <span className="truncate">
                    {other?.title || other?.body_preview?.slice(0, 40) || otherId}
                    {other?.community_id && other.community_id !== node.community_id && (
                      <span className="text-gray-600 ml-1">
                        [{data.communities?.find(c => c.id === other.community_id)?.name || "other"}]
                      </span>
                    )}
                  </span>
```

- [ ] **Step 4: Commit**

```bash
cd .worktrees/knowledge-graph
git add frontend/src/components/knowledge-graph/detail-panel.tsx
git commit -m "fix: detail panel D3 mutation bug and add cross-community labels"
```

### Task 4: Rewrite sidebar with functional filters

The current sidebar has decorative checkboxes that don't filter anything. Rewrite it to accept and update `GraphFilterState`.

**Files:**
- Rewrite: `.worktrees/knowledge-graph/frontend/src/components/knowledge-graph/graph-sidebar.tsx`

- [ ] **Step 1: Rewrite graph-sidebar.tsx**

```typescript
"use client";
import { GraphResponse, FrontierResponse, GraphFilterState, FrontierStatus, GraphNode } from "@/lib/types";

const STATUS_COLORS: Record<FrontierStatus, string> = {
  frontier: "#6f6fd0",
  debated: "#d06f6f",
  resolved: "#4aad4a",
  explored: "#555",
  isolated: "#333",
};

const EDGE_COLORS: Record<string, string> = {
  extends: "#6f6fd0",
  contradicts: "#d06f6f",
  references: "#6fd06f",
  solves: "#d0ad6f",
  repost: "#888",
};

interface Props {
  data: GraphResponse;
  frontier: FrontierResponse | null;
  filters: GraphFilterState;
  onFiltersChange: (filters: GraphFilterState) => void;
  classifyNode: (node: GraphNode) => FrontierStatus;
}

export default function GraphSidebar({ data, frontier, filters, onFiltersChange, classifyNode }: Props) {
  const questions = data.nodes.filter(n => n.type === "question");

  // Count statuses
  const statusCounts: Record<FrontierStatus, number> = {
    frontier: 0, debated: 0, resolved: 0, explored: 0, isolated: 0,
  };
  for (const q of questions) {
    statusCounts[classifyNode(q)]++;
  }

  // Count edge types (non-structural only)
  const edgeCounts: Record<string, number> = {};
  for (const edge of data.edges) {
    if (edge.edge_type !== "structural") {
      edgeCounts[edge.edge_type] = (edgeCounts[edge.edge_type] || 0) + 1;
    }
  }

  const toggle = (key: keyof GraphFilterState) => {
    onFiltersChange({ ...filters, [key]: !filters[key as keyof GraphFilterState] });
  };

  const statusFilters: { key: keyof GraphFilterState; label: string; status: FrontierStatus }[] = [
    { key: "showFrontier", label: "Frontier", status: "frontier" },
    { key: "showDebated", label: "Debated", status: "debated" },
    { key: "showResolved", label: "Resolved", status: "resolved" },
    { key: "showExplored", label: "Explored", status: "explored" },
    { key: "showIsolated", label: "Isolated", status: "isolated" },
  ];

  const linkFilters: { key: keyof GraphFilterState; label: string; type: string }[] = [
    { key: "showExtends", label: "extends", type: "extends" },
    { key: "showContradicts", label: "contradicts", type: "contradicts" },
    { key: "showReferences", label: "references", type: "references" },
    { key: "showSolves", label: "solves", type: "solves" },
    { key: "showRepost", label: "repost", type: "repost" },
  ];

  return (
    <div className="w-[260px] border-r border-gray-800 bg-gray-950 overflow-y-auto p-4 flex flex-col gap-5">
      {/* Overview stats */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Overview</h3>
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">{questions.length}</div>
            <div className="text-[10px] text-gray-500">Questions</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">
              {data.edges.filter(e => e.edge_type !== "structural").length}
            </div>
            <div className="text-[10px] text-gray-500">Links</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">{data.communities.length}</div>
            <div className="text-[10px] text-gray-500">Communities</div>
          </div>
        </div>
      </div>

      {/* Status filters */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Status</h3>
        <div className="flex flex-col gap-1.5">
          {statusFilters.map(({ key, label, status }) => (
            <label key={key} className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
              <input
                type="checkbox"
                checked={filters[key] as boolean}
                onChange={() => toggle(key)}
                className="rounded"
              />
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: STATUS_COLORS[status] }} />
              {label} ({statusCounts[status]})
            </label>
          ))}
        </div>
      </div>

      {/* Quick views */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Quick Views</h3>
        <div className="flex flex-col gap-1.5">
          <button
            onClick={() => onFiltersChange({
              ...filters,
              showFrontier: true, showDebated: true,
              showResolved: false, showExplored: false, showIsolated: false,
            })}
            className="text-left text-xs px-2 py-1.5 rounded bg-gray-900 border border-gray-800 text-gray-400 hover:text-gray-200 hover:border-gray-700"
          >
            Show only frontier + debated
          </button>
          <button
            onClick={() => {
              // Find nodes that have cross-community edges
              const crossEdgeNodeIds = new Set<string>();
              const nodeMap = new Map(data.nodes.map(n => [n.id, n]));
              for (const edge of data.edges) {
                if (edge.edge_type === "structural") continue;
                const src = nodeMap.get(edge.source);
                const tgt = nodeMap.get(edge.target);
                if (src && tgt && src.community_id !== tgt.community_id) {
                  crossEdgeNodeIds.add(src.id);
                  crossEdgeNodeIds.add(tgt.id);
                }
              }
              // This sets a transient filter — implementation can use a separate
              // "highlightNodeIds" state or filter to only these nodes
              onFiltersChange({
                ...filters,
                showFrontier: true, showDebated: true,
                showResolved: true, showExplored: true, showIsolated: true,
              });
              // Note: the full cross-community filter needs a highlightNodeIds
              // field or similar in GraphFilterState. For v1, this button
              // shows all nodes but the implementing agent should add visual
              // emphasis (brighter opacity) to cross-community-linked nodes.
            }}
            className="text-left text-xs px-2 py-1.5 rounded bg-gray-900 border border-gray-800 text-gray-400 hover:text-gray-200 hover:border-gray-700"
          >
            Show only cross-community links
          </button>
          <button
            onClick={() => onFiltersChange({
              ...filters,
              showFrontier: true, showDebated: true,
              showResolved: true, showExplored: true, showIsolated: true,
            })}
            className="text-left text-xs px-2 py-1.5 rounded bg-gray-900 border border-gray-800 text-gray-400 hover:text-gray-200 hover:border-gray-700"
          >
            Show all
          </button>
        </div>
      </div>

      {/* Link type filters */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Link Types</h3>
        <div className="flex flex-col gap-1.5">
          {linkFilters.map(({ key, label, type }) => (
            <label key={key} className="flex items-center justify-between text-xs text-gray-400 cursor-pointer">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={filters[key] as boolean}
                  onChange={() => toggle(key)}
                  className="rounded"
                />
                <span className="w-3 h-0.5 rounded" style={{ background: EDGE_COLORS[type] || "#555" }} />
                {label}
              </div>
              <span className="text-gray-600">{edgeCounts[type] || 0}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Communities list */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">
          Communities ({data.communities.length})
        </h3>
        <div className="flex flex-col gap-1.5">
          {filters.view === "community" && (
            <button
              onClick={() => onFiltersChange({ ...filters, view: "overview", selectedCommunityId: null })}
              className="text-left text-xs text-blue-400 hover:text-blue-300 mb-1"
            >
              ← All Communities
            </button>
          )}
          {data.communities.map(community => {
            const count = questions.filter(q => q.community_id === community.id).length;
            return (
              <button
                key={community.id}
                onClick={() => onFiltersChange({
                  ...filters,
                  view: "community",
                  selectedCommunityId: community.id,
                })}
                className={`text-left text-xs px-2 py-1 rounded flex justify-between ${
                  filters.selectedCommunityId === community.id
                    ? "bg-gray-800 text-gray-200"
                    : "text-gray-400 hover:text-gray-300 hover:bg-gray-900"
                }`}
              >
                <span className="truncate">{community.name}</span>
                <span className="text-gray-600 ml-2">{count}</span>
              </button>
            );
          })}
          {/* Uncategorized */}
          {(() => {
            const uncatCount = questions.filter(q => !q.community_id).length;
            if (uncatCount === 0) return null;
            return (
              <button
                onClick={() => onFiltersChange({
                  ...filters,
                  view: "community",
                  selectedCommunityId: "__uncategorized__",
                })}
                className={`text-left text-xs px-2 py-1 rounded flex justify-between ${
                  filters.selectedCommunityId === "__uncategorized__"
                    ? "bg-gray-800 text-gray-200"
                    : "text-gray-400 hover:text-gray-300 hover:bg-gray-900"
                }`}
              >
                <span className="truncate italic">Uncategorized</span>
                <span className="text-gray-600 ml-2">{uncatCount}</span>
              </button>
            );
          })()}
        </div>
      </div>

      {/* Agents (drill-down only) */}
      {filters.view === "community" && (
        <div>
          <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Agents ({data.agents.length})</h3>
          <div className="flex flex-col gap-1.5">
            {data.agents.map((agent, i) => {
              const palette = ["#4aad4a", "#ad4a4a", "#4a4aad", "#d0ad6f", "#4aadad", "#ad4aad"];
              return (
                <div key={agent.id} className="flex items-center gap-2 text-xs text-gray-400">
                  <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: palette[i % palette.length] }} />
                  <span className="truncate">{agent.display_name}</span>
                  <span className="text-gray-600 ml-auto">{agent.kind}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
cd .worktrees/knowledge-graph
git add frontend/src/components/knowledge-graph/graph-sidebar.tsx
git commit -m "feat: rewrite sidebar with functional status and link type filters"
```

---

## Chunk 3: Graph View Rewrite (Overview)

### Task 5: Rewrite connections-view.tsx for overview mode

The main graph rewrite: questions only, semantic edges, community gravity wells, status colors, hover tooltips.

**Files:**
- Rewrite: `.worktrees/knowledge-graph/frontend/src/components/knowledge-graph/connections-view.tsx`

- [ ] **Step 1: Create the classification helper (named export)**

Add to the top of `connections-view.tsx`. This is a **named export** — the page component imports it as `{ classifyNode }`. The default export remains the component itself. Both must survive the rewrite in Step 2.

```typescript
import { GraphNode, GraphResponse, FrontierResponse, GraphFilterState, FrontierStatus } from "@/lib/types";

export function classifyNode(
  node: GraphNode,
  frontierIds: Set<string>,
  debateIds: Set<string>,
  isolatedIds: Set<string>,
): FrontierStatus {
  if (frontierIds.has(node.id)) return "frontier";
  if (debateIds.has(node.id)) return "debated";
  if (isolatedIds.has(node.id)) return "isolated";
  if (node.status === "resolved") return "resolved";
  return "explored";
}
```

- [ ] **Step 2: Write the full overview graph component**

> **Note for implementers:** This task is the most complex in the plan. The code below provides the architectural skeleton, key constants, force simulation setup, tooltip pattern, and Props interface. The implementing agent must compose these into a complete ~250-line React component with a `useEffect` that builds the D3 visualization. Use the current `connections-view.tsx` as a structural reference for the SVG setup, zoom behavior, drag handlers, and tick function pattern. The key differences from the current implementation are listed below.

Rewrite `connections-view.tsx` entirely. Key changes from current:
- Filter to question nodes only at overview level
- Apply status filters from `GraphFilterState`
- Apply link type filters (exclude structural, filter by type visibility)
- Color nodes by frontier status, not content type
- Community gravity wells via `d3.forceX`/`d3.forceY` per community
- Subtle halo ellipses behind community clusters
- Cross-community edges: bold, dashed, stroke-width 3
- Hover tooltip (positioned div, shows title + status + answer count + score)
- Click node → `onSelectNode`
- Click halo/community area → `onSelectCommunity`
- Answer count badge on each question node
- Pulsing ring animation for frontier nodes

The full component code is large (~250 lines). Key constants:

```typescript
const STATUS_COLORS: Record<FrontierStatus, { fill: string; stroke: string }> = {
  frontier: { fill: "#1a1a3a", stroke: "#6f6fd0" },
  debated:  { fill: "#3a1a1a", stroke: "#d06f6f" },
  resolved: { fill: "#1a3a1a", stroke: "#4aad4a" },
  explored: { fill: "#1a1a1a", stroke: "#555555" },
  isolated: { fill: "#111111", stroke: "#333333" },
};

const EDGE_COLORS: Record<string, string> = {
  extends: "#6f6fd0", contradicts: "#d06f6f", references: "#6fd06f",
  solves: "#d0ad6f", repost: "#888888", structural: "#333333",
};
```

Force simulation setup:

```typescript
// Compute community centers for gravity wells
const communityNodes = new Map<string, { x: number; y: number }>();
const commIds = [...new Set(filteredNodes.map(n => n.community_id || "__uncategorized__"))];
commIds.forEach((cid, i) => {
  const angle = (2 * Math.PI * i) / commIds.length;
  const radius = Math.min(width, height) * 0.3;
  communityNodes.set(cid, {
    x: width / 2 + radius * Math.cos(angle),
    y: height / 2 + radius * Math.sin(angle),
  });
});

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(edges).id((d: any) => d.id).distance(120))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("x", d3.forceX((d: any) => {
    const center = communityNodes.get(d.community_id || "__uncategorized__");
    return center?.x ?? width / 2;
  }).strength(0.3))
  .force("y", d3.forceY((d: any) => {
    const center = communityNodes.get(d.community_id || "__uncategorized__");
    return center?.y ?? height / 2;
  }).strength(0.3))
  .force("collision", d3.forceCollide().radius(22));
```

Tooltip implementation:

```typescript
// Tooltip div (append to container, not SVG)
const tooltip = d3.select(containerRef.current)
  .append("div")
  .attr("class", "absolute pointer-events-none bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs hidden z-50")
  .style("max-width", "200px");

// On node mouseover
node.on("mouseover", (event: any, d: any) => {
  tooltip
    .classed("hidden", false)
    .html(`
      <div class="font-semibold text-gray-200 mb-1">${d.title?.slice(0, 60) || "Untitled"}</div>
      <div class="text-gray-400">Status: <span style="color:${STATUS_COLORS[d._status].stroke}">${d._status}</span></div>
      <div class="text-gray-400">Answers: ${d.answer_count ?? 0} · Score: ${d.score}</div>
    `)
    .style("left", `${event.offsetX + 15}px`)
    .style("top", `${event.offsetY - 10}px`);
})
.on("mouseout", () => tooltip.classed("hidden", true));
```

Props interface:

```typescript
interface Props {
  data: GraphResponse;
  frontier: FrontierResponse | null;
  filters: GraphFilterState;
  onSelectNode: (node: GraphNode | null) => void;
  onSelectCommunity: (communityId: string) => void;
}
```

- [ ] **Step 3: Verify it renders**

Run: `cd .worktrees/knowledge-graph/frontend && npm run build`
Expected: Build succeeds with no errors

- [ ] **Step 4: Commit**

```bash
cd .worktrees/knowledge-graph
git add frontend/src/components/knowledge-graph/connections-view.tsx
git commit -m "feat: rewrite graph view with status colors, gravity wells, tooltips"
```

---

## Chunk 4: Community Drill-down + Page Assembly

### Task 6: Add community drill-down mode to graph view

When `filters.view === "community"`, show all nodes (questions + answers + reviews) for the selected community with structural edges, agent dots, and verdict badges.

**Files:**
- Modify: `.worktrees/knowledge-graph/frontend/src/components/knowledge-graph/connections-view.tsx`

- [ ] **Step 1: Add drill-down rendering branch**

Inside `connections-view.tsx`, after the overview rendering logic, add a conditional branch:

```typescript
if (filters.view === "community" && filters.selectedCommunityId) {
  // Filter nodes: questions in this community + their answers + their comments
  const communityQuestionIds = new Set(
    data.nodes
      .filter(n => n.type === "question" && (
        filters.selectedCommunityId === "__uncategorized__"
          ? !n.community_id
          : n.community_id === filters.selectedCommunityId
      ))
      .map(n => n.id)
  );
  const communityAnswerIds = new Set(
    data.nodes
      .filter(n => n.type === "answer" && n.question_id && communityQuestionIds.has(n.question_id))
      .map(n => n.id)
  );
  const communityNodes = data.nodes.filter(n =>
    communityQuestionIds.has(n.id) ||
    communityAnswerIds.has(n.id) ||
    (n.type === "comment" && n.answer_id && communityAnswerIds.has(n.answer_id))
  );

  const communityNodeIds = new Set(communityNodes.map(n => n.id));

  // Include ALL edges between community nodes (structural + semantic)
  const communityEdges = data.edges.filter(e => {
    const srcId = typeof e.source === "object" ? (e.source as any).id : e.source;
    const tgtId = typeof e.target === "object" ? (e.target as any).id : e.target;
    return communityNodeIds.has(srcId) && communityNodeIds.has(tgtId);
  });

  // Cross-community edges: one end in this community, other end outside
  // Render these as lines that go off-screen with a text label
  const crossCommunityEdges = data.edges.filter(e => {
    if (e.edge_type === "structural") return false;
    const srcId = typeof e.source === "object" ? (e.source as any).id : e.source;
    const tgtId = typeof e.target === "object" ? (e.target as any).id : e.target;
    const srcIn = communityNodeIds.has(srcId);
    const tgtIn = communityNodeIds.has(tgtId);
    return (srcIn && !tgtIn) || (!srcIn && tgtIn);
  });
}
```

Rendering differences for drill-down mode:
- **Node colors:** Questions use status colors (same as overview). Answers: fill `#1a1a2a`, stroke `#4a4aad`. Comments: fill `#2a2a1a`, stroke `#ad8a4a`.
- **Agent color dots:** 4px circle at top-right of each answer/comment node. Use the same palette as current: `["#4aad4a", "#ad4a4a", "#4a4aad", "#d0ad6f", "#4aadad", "#ad4aad"]`, indexed by agent position in `data.agents`.
- **Verdict badges:** For comment nodes with `verdict`, render a text element below the node: `✓ correct` (green), `✗ incorrect` (red), `~ unsure` (gold), `? partially_correct` (yellow).
- **Structural edges:** `stroke: #333`, `stroke-width: 1.5`, `opacity: 0.4`.
- **Semantic edges:** Same colors as overview, normal weight.
- **Cross-community edges:** Render as a line from the local node toward the edge of the SVG. Add a text label at the end: `"→ {community_name}"` using `data.communities.find(c => c.id === otherNode.community_id)?.name`.
- **Force simulation:** Standard charge + collision, no community gravity wells (single community). Use `d3.forceLink` with shorter distance for structural edges (40px) and longer for semantic (120px), same as current.
```

Key differences from overview:
- Show all node types (question, answer, comment)
- Include structural edges (thin, gray, low opacity)
- Agent color dots on answers/reviews (4px circles at top-right of node)
- Verdict text under review nodes
- Question nodes still colored by frontier status
- Answer nodes: indigo fill `#1a1a2a`, stroke `#4a4aad`
- Comment nodes: amber fill `#2a2a1a`, stroke `#ad8a4a`
- Cross-community edges trail off-screen with destination label
- No community gravity wells (single community)

- [ ] **Step 2: Add breadcrumb to the graph**

Render a breadcrumb overlay at top of the graph area:

```typescript
// In the JSX return, before the SVG:
{filters.view === "community" && (
  <div className="absolute top-3 left-3 z-10 flex items-center gap-2 text-sm">
    <button
      onClick={() => onSelectCommunity("")}
      className="text-blue-400 hover:text-blue-300"
    >
      ← All Communities
    </button>
    <span className="text-gray-600">/</span>
    <span className="text-gray-300">
      {data.communities.find(c => c.id === filters.selectedCommunityId)?.name || "Uncategorized"}
    </span>
  </div>
)}
```

- [ ] **Step 3: Verify build**

Run: `cd .worktrees/knowledge-graph/frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 4: Commit**

```bash
cd .worktrees/knowledge-graph
git add frontend/src/components/knowledge-graph/connections-view.tsx
git commit -m "feat: add community drill-down with structural edges and agent dots"
```

### Task 7: Rewire analytics page and delete frontier map

Wire everything together in the page component. Delete the frontier map.

**Files:**
- Rewrite: `.worktrees/knowledge-graph/frontend/src/app/analytics/page.tsx`
- Delete: `.worktrees/knowledge-graph/frontend/src/components/knowledge-graph/frontier-map.tsx`

- [ ] **Step 1: Rewrite analytics page**

```typescript
"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { analytics } from "@/lib/api";
import {
  GraphResponse, FrontierResponse, GraphNode, GraphFilterState,
  DEFAULT_FILTERS, FrontierStatus
} from "@/lib/types";
import ConnectionsView, { classifyNode } from "@/components/knowledge-graph/connections-view";
import GraphSidebar from "@/components/knowledge-graph/graph-sidebar";
import DetailPanel from "@/components/knowledge-graph/detail-panel";

export default function AnalyticsPage() {
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [frontierData, setFrontierData] = useState<FrontierResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<GraphFilterState>(DEFAULT_FILTERS);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [graph, frontier] = await Promise.all([
          analytics.graph(),
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
  }, []);

  // Build classification sets from frontier data (memoized to avoid new Set per render)
  const { frontierIds, debateIds, isolatedIds } = useMemo(() => ({
    frontierIds: new Set(frontierData?.frontier_questions.map(q => q.id) ?? []),
    debateIds: new Set(frontierData?.active_debates.map(d => d.question_id) ?? []),
    isolatedIds: new Set(frontierData?.isolated_questions.map(q => q.id) ?? []),
  }), [frontierData]);

  const classify = useCallback((node: GraphNode): FrontierStatus => {
    return classifyNode(node, frontierIds, debateIds, isolatedIds);
  }, [frontierIds, debateIds, isolatedIds]);

  const selectedNode = graphData?.nodes.find(n => n.id === filters.selectedNodeId) ?? null;

  if (error) return <div className="p-8 text-red-400">{error}</div>;
  if (loading || !graphData) return <div className="p-8 text-gray-500">Loading graph...</div>;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center px-5 py-3 border-b border-gray-800">
        <h1 className="text-lg font-semibold">Knowledge Graph</h1>
      </div>
      <div className="flex flex-1 overflow-hidden">
        <GraphSidebar
          data={graphData}
          frontier={frontierData}
          filters={filters}
          onFiltersChange={setFilters}
          classifyNode={classify}
        />
        <div className="flex-1 overflow-hidden">
          <ConnectionsView
            data={graphData}
            frontier={frontierData}
            filters={filters}
            onSelectNode={(node) => setFilters(f => ({ ...f, selectedNodeId: node?.id ?? null }))}
            onSelectCommunity={(cid) => setFilters(f => ({
              ...f,
              view: cid ? "community" : "overview",
              selectedCommunityId: cid || null,
            }))}
          />
        </div>
        {selectedNode && (
          <DetailPanel
            node={selectedNode}
            data={graphData}
            onClose={() => setFilters(f => ({ ...f, selectedNodeId: null }))}
          />
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Delete frontier-map.tsx**

```bash
cd .worktrees/knowledge-graph
rm frontend/src/components/knowledge-graph/frontier-map.tsx
```

- [ ] **Step 3: Verify build**

Run: `cd .worktrees/knowledge-graph/frontend && npm run build`
Expected: Build succeeds, no references to FrontierMap

- [ ] **Step 4: Commit**

```bash
cd .worktrees/knowledge-graph
git add -A frontend/src/app/analytics/page.tsx frontend/src/components/knowledge-graph/frontier-map.tsx
git commit -m "feat: wire up graph page with filters, delete frontier map"
```

---

## Chunk 5: Manual Testing + Polish

### Task 8: Deploy and test on server

**Files:** None (testing only)

- [ ] **Step 1: Build frontend**

```bash
cd .worktrees/knowledge-graph/frontend
npm run build
```

Expected: Clean build, no errors

- [ ] **Step 2: Deploy to server and test**

Push the knowledge-graph branch, pull on server, rebuild. Test these scenarios:

1. Overview loads — question nodes grouped by community with halos and labels
2. Node colors match frontier status (blue pulsing = frontier, red = debated, green = resolved)
3. Semantic edges visible, no structural edges at overview
4. Cross-community links are bold dashed lines
5. Hover shows tooltip with title, status, answer count
6. Click node opens detail panel with correct connections list
7. Click community zooms to drill-down with answers/reviews/agent dots
8. Breadcrumb returns to overview
9. Sidebar status filters actually hide/show nodes
10. Sidebar link type filters work
11. "Show only frontier + debated" quick view works
12. Community list in sidebar allows navigation

- [ ] **Step 3: Fix any issues found during testing**

- [ ] **Step 4: Final commit**

```bash
cd .worktrees/knowledge-graph
git add -A
git commit -m "fix: polish graph visualization after manual testing"
```
