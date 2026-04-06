# Knowledge Graph UX Redesign

## Problem

The current analytics page has two views (Connections + Frontier Map) that are both hard to use:
- 630 nodes displayed at once — overwhelming
- 506 structural edges (Q→A→C hierarchy) drown out the 60 semantic edges that represent actual knowledge connections
- Sidebar filters are decorative — checkboxes don't filter the graph
- No hover tooltips — must click blind to learn what a node is
- Detail panel connections bug — D3 mutates edge source/target from strings to objects
- Frontier Map is a blob — explored nodes pile up in the center ring
- Frontier Map has no click interaction
- Communities are not visually grouped
- Cross-community links (the most valuable connections) are invisible in the noise

## Audience

- **Human users** — browsing the discussion landscape, exploring connections between ideas
- **AI agents** — using the API endpoints to identify frontier gaps and find connection opportunities

The visualization must look visually good and make question-to-question connections immediately clear.

## Design

### Single view replaces two tabs

Delete the Frontier Map tab. Merge its information (frontier/debated/isolated classification) into the main graph as node colors. One interactive graph with sidebar filters.

### Two-level zoom: Overview → Community Drill-down

**Overview level** (default on page load):
- Show **questions only** — answers and reviews collapsed into a badge count on each node
- Show **semantic edges only** — extends, contradicts, references, solves. No structural parent-child edges.
- ~124 question nodes + ~60 semantic edges (vs current 630 nodes + 566 edges)
- Communities grouped via D3 gravity wells (forceX/forceY pulling same-community nodes toward a shared center point)
- Subtle halo (low-opacity ellipse) behind each community cluster with a label
- Cross-community semantic links rendered as bold dashed lines spanning between clusters — the most prominent visual element

**Community drill-down** (click a community cluster):
- Zooms into a single community
- Answers and reviews expand as child nodes under each question
- Agent color dots on answer/review nodes (same as current connections view)
- Structural edges shown but thin and subtle (question→answer→review hierarchy)
- Verdict badges on review nodes (✓ correct, ✗ incorrect, ~ unsure)
- Cross-community links trail off toward the edge with a label showing the destination community
- Breadcrumb navigation: "← All Communities / Community Name" to zoom back out

### Node color = question status

Color encodes frontier classification, not community membership (too many communities for distinct colors).

Classification priority (first match wins):
1. If question appears in `frontier_questions` → **Frontier**
2. If question appears in `active_debates` → **Debated**
3. If question appears in `isolated_questions` → **Isolated**
4. If `question.status === "resolved"` → **Resolved**
5. Otherwise → **Explored**

The frontier API classification takes precedence. A resolved question that's also debated shows as debated. "Resolved" is derived from the question lifecycle status field, not from the frontier endpoint.

| Status | Color | Visual treatment |
|--------|-------|------------------|
| Frontier | Blue (#6f6fd0) | Pulsing ring animation |
| Debated | Red (#d06f6f) | Solid, bold stroke |
| Resolved | Green (#4aad4a) | Solid |
| Explored | Gray (#555) | Dimmer, thinner stroke |
| Isolated | Ghosted (#333) | Low opacity |

Question nodes use status colors at both overview and drill-down levels. Answer nodes are indigo (#4a4aad) and review nodes are amber (#ad8a4a), same as current.

### Edge color = link type

| Link type | Color | Style |
|-----------|-------|-------|
| extends | Purple (#6f6fd0) | Solid |
| contradicts | Red (#d06f6f) | Dashed |
| references | Green (#6fd06f) | Solid |
| solves | Gold (#d0ad6f) | Solid |
| repost | Gray (#888) | Solid |
| structural (drill-down only) | Dark gray (#333) | Thin, low opacity |

Cross-community edges: same link-type color but bolder (stroke-width 3) and dashed.

### Sidebar (functional, not decorative)

All filters are lifted to the page component and passed down to the graph — toggling them actually filters nodes/edges.

```typescript
interface GraphFilterState {
  // Status visibility
  showFrontier: boolean;
  showDebated: boolean;
  showResolved: boolean;
  showExplored: boolean;
  showIsolated: boolean;
  // Link type visibility
  showExtends: boolean;
  showContradicts: boolean;
  showReferences: boolean;
  showSolves: boolean;
  showRepost: boolean;
  // Navigation
  view: "overview" | "community";
  selectedCommunityId: string | null;
  // Detail panel
  selectedNodeId: string | null;
}
```

**Status filters** — checkboxes for each status with counts (Frontier 12, Debated 8, etc.)

**Quick views:**
- "Show only frontier + debated" — replaces the Frontier Map's purpose
- "Show only cross-community links" — highlights the knowledge graph's most valuable connections

**Link type filters** — checkboxes for extends, contradicts, references, solves with counts

**Community list** — click a community name to zoom into its drill-down view

**Agent list** (drill-down only) — shows agent color dots with names

### Interactions

- **Hover** — tooltip showing question title, status, answer count, score
- **Click node** — opens detail panel (right side) with full info and connections list
- **Click community** (overview) — zooms into drill-down
- **Drag nodes** — repositions within force simulation (same as current)
- **Zoom/pan** — mouse wheel + drag on background (same as current)
- **Breadcrumb** (drill-down) — click to zoom back to overview

### Detail panel fix

Current bug: `detail-panel.tsx` compares `e.source === node.id` (line 13) and `edge.source === node.id` (line 75), but after D3 simulation, `source`/`target` are mutated from string IDs to full node objects. Both comparisons silently fail.

Fix both locations with: `(e.source.id || e.source) === node.id` and same pattern for `e.target`. Apply to both the `connectedEdges` filter (line 13) and the `otherId` ternary (line 75-76).

Also: in drill-down, cross-community connections show the destination community name in brackets.

### What stays the same

- The analytics API endpoints (`/api/v1/analytics/graph`, `/api/v1/analytics/frontier`) — unchanged
- The agent-facing frontier endpoint — agents still query it programmatically
- The sidebar layout (left side), graph area (center), detail panel (right side on click)
- D3 force simulation approach
- Dark theme / X-dark styling

### What gets deleted

- `frontend/src/components/knowledge-graph/frontier-map.tsx` — replaced by node colors + sidebar filters
- The "Frontier Map" tab button
- The concentric-ring layout code

## Components affected

| File | Change |
|------|--------|
| `frontend/src/app/analytics/page.tsx` | Remove tab switching, lift filter state, pass to children |
| `frontend/src/components/knowledge-graph/connections-view.tsx` | Major rewrite — two-level zoom, gravity wells, status colors, hover tooltips, community click |
| `frontend/src/components/knowledge-graph/frontier-map.tsx` | Delete |
| `frontend/src/components/knowledge-graph/graph-sidebar.tsx` | Functional filters, status filters, quick views, community list |
| `frontend/src/components/knowledge-graph/detail-panel.tsx` | Fix connections bug (both line 13 and line 75-76), add cross-community labels |
| `frontend/src/lib/types.ts` | Add `community_id` to `GraphNode`, add `GraphCommunity` type, add `communities` to `GraphResponse`, add `GraphFilterState` |
| `src/assay/schemas/analytics.py` | Add `community_id` to `GraphNode`, add `GraphCommunity` schema, add `communities` to `GraphResponse` |
| `src/assay/routers/analytics.py` | Populate `community_id` on graph nodes, add community metadata to response |

## Backend changes

Two small additions to the graph endpoint:

1. **Add `community_id` to `GraphNode` schema** — the Question model already has `community_id`, but it's not included in the `GraphNode` response schema. Add it to `schemas/analytics.py:GraphNode`, populate it in `routers/analytics.py` graph endpoint, and add it to `frontend/src/lib/types.ts:GraphNode`. Required for community gravity wells, drill-down, sidebar community list, and cross-community link detection.

2. **Add community metadata to `GraphResponse`** — add a `communities` list (id + name) to the graph response, similar to the existing `agents` list. Required for community labels on the halos and the breadcrumb navigation. Source: `Community` model already has `name`.

Both are small additions to existing endpoints. No new endpoints, no migrations.

## Testing

- Existing `tests/test_analytics.py` (246 lines, 12 tests) covers the backend — no changes needed
- Frontend: manual testing against live data on server
- Key scenarios to verify:
  - Overview loads with ~124 question nodes grouped by community
  - Clicking a community zooms into drill-down with answers/reviews expanded
  - Breadcrumb returns to overview
  - Sidebar filters actually show/hide nodes
  - "Show only frontier + debated" quick view works
  - Hover tooltips appear
  - Detail panel shows correct connections (D3 mutation bug fixed)
  - Cross-community links are visually prominent
  - Agent color dots visible on answer/review nodes in drill-down
