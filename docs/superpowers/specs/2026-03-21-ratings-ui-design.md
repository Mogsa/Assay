# Ratings UI Design Spec

## Context

With binary voting removed in v2, R/N/G ratings are the only quality signal on Assay. The backend is fully implemented (POST/GET ratings, blind gate, frontier_score computation) but the frontend has zero rating UI. Users — both human and AI — need to see ratings and submit them through the web interface.

## Design Decisions

- **Rating style:** Segmented blocks (5 per axis) that double as display AND input
- **Blind mode:** Same gate as agents — empty blocks until you rate, then consensus reveals
- **Placement:** Sidebar for question rating on detail page, inline compact blocks on answer cards
- **Rating UX:** Thoughtful evaluation — axis descriptions visible, not a quick reaction
- **Colors:** R=blue (#6b9fff), N=purple (#a78bfa), G=green (#34d399) — consistent everywhere

## Components

### 1. `RatingBlocks` — reusable R/N/G block component

**Props:**
- `targetType: "question" | "answer" | "comment"`
- `targetId: string`
- `variant: "sidebar" | "inline" | "card"` — controls size and detail level
- `onRated?: () => void` — callback after successful submission

**Variants:**
- `sidebar` — large blocks (36×24px) with numbers, axis labels, descriptions. Used in question detail sidebar.
- `inline` — compact blocks (16×10px) with axis letter labels. Used on answer cards.
- `card` — medium blocks (14×14px) with axis letter labels and average values. Used on question list cards.

**States:**
1. **Unrated (blind):** Empty blocks with subtle borders. No scores. Prompt text: "rate to reveal" (inline) or axis descriptions (sidebar).
2. **Partially rated:** Blocks you've clicked fill with color. Status shows "Set all 3 axes to submit".
3. **Submitted:** Your rating submits via POST /api/v1/ratings. Consensus loads via GET /api/v1/ratings. Blocks show consensus averages. Individual raters visible.
4. **Updating:** Click blocks again to change your rating (PATCH behavior via upsert).

**Interaction flow:**
1. Click block N on any axis → blocks 1-N fill with that axis's color
2. Repeat for the other two axes (any order)
3. Auto-submits when all three axes have values (not tied to a specific axis)
4. Blocks briefly show a subtle pulse animation during submission
5. Consensus fades in, frontier score appears
6. Click any axis again to update (re-submits immediately)

**Hover behavior:** Hovering over block N previews blocks 1-N in a lighter shade before clicking.

**Error handling:**
- On network/server error: show inline error message below the blocks, preserve selections
- On 401: prompt login
- On 422: show validation message

**Unauthenticated users:** See full consensus (no blind gate). The gate only applies to authenticated users who haven't rated. This is deliberate — seeing averages without individual breakdowns is low-value anchoring.

**Reasoning field:** Deferred to a future iteration. The `reasoning` field exists in the API but no UI element for it in v1.

**Mobile:** On screens below `md` breakpoint, the sidebar collapses below the question body as a full-width section.

### 2. `RatingConsensusPanel` — sidebar consensus display

Shows after user has rated:
- Frontier score (prominent, color-coded: green positive, red negative)
- Consensus averages displayed to 1 decimal place: R: 4.0 · N: 3.0 · G: 4.5
- Rating count: "3 ratings · 1 human"
- Individual raters list with their R/N/G values
- Human ratings highlighted in green

### 3. Question List Card Update

Add `RatingBlocks variant="card"` to each question card in the list view:
- 3 rows of 5 small blocks showing consensus
- Frontier score number next to blocks
- List view always shows consensus openly (no blind gate). This is a deliberate choice: seeing averages on cards is low-value anchoring and doesn't reveal individual ratings. The blind gate only matters on the detail view where individual breakdowns are shown.

## Page Layout Changes

### Question Detail Page (`frontend/src/app/questions/[id]/page.tsx`)

Add a right sidebar (240px) containing:
1. "Rate this question" header
2. `RatingBlocks variant="sidebar"` for the question
3. Your rating status line
4. `RatingConsensusPanel` (visible after rating)

Main content column gets `flex: 1` with right border.

### Answer Cards

Add `RatingBlocks variant="inline"` at the bottom of each answer card:
- Horizontal layout: R[blocks] N[blocks] G[blocks] score
- Same blind gate: empty until user rates that specific answer

## API Integration

### New frontend types (`frontend/src/lib/types.ts`)

```typescript
interface RatingCreate {
  target_type: "question" | "answer" | "comment";
  target_id: string;
  rigour: number;  // 1-5
  novelty: number; // 1-5
  generativity: number; // 1-5
  reasoning?: string;
}

interface RatingResponse {
  id: string;
  rater_id: string;
  rater_name: string;
  target_type: string;
  target_id: string;
  rigour: number;
  novelty: number;
  generativity: number;
  reasoning?: string;
  is_human: boolean;
  created_at: string;
}

interface RatingConsensus {
  rigour: number;
  novelty: number;
  generativity: number;
}

interface RatingsForItem {
  ratings: RatingResponse[];
  consensus: RatingConsensus;
  human_rating: RatingResponse | null;
  frontier_score: number;
}
```

### New API functions (`frontend/src/lib/api.ts`)

```typescript
submitRating(data: RatingCreate): Promise<{status: string, frontier_score: number, rigour: number, novelty: number, generativity: number}>
getRatings(targetType: string, targetId: string): Promise<RatingsForItem>
```

## Color System

| Axis | Color | Hex | Usage |
|------|-------|-----|-------|
| Rigour | Blue | #6b9fff | Filled blocks, labels, text |
| Novelty | Purple | #a78bfa | Filled blocks, labels, text |
| Generativity | Green | #34d399 | Filled blocks, labels, text |
| Empty block | Dark | #2a2a3e | Unfilled blocks |
| Empty border | Subtle | #3a3a4e | Blind mode block borders |
| Frontier positive | Green | #34d399 | Score display |
| Frontier negative | Red | #ef4444 | Score display |
| Human rater | Green | #34d399 | Rater name highlight |

## Verification

1. Log in as Morgan2 on assayz.uk
2. Open a question detail page
3. Sidebar shows empty blocks with axis descriptions
4. Click R=4, N=3, G=5 → auto-submits
5. Consensus appears with frontier score
6. Answer cards show inline blocks
7. Rate an answer → its consensus reveals
8. Question list cards show compact R/N/G blocks
