# Ratings UI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace binary voting UI with R/N/G rating blocks across the entire frontend — main feed, question detail, and answer cards. Add links tab to question detail page. Remove all vote-related code.

**Architecture:** One reusable `RatingBlocks` component with 3 size variants (card/question/inline). Data flows through new rating API functions. Vote arrows, vote handlers, and vote API calls are deleted. Links tab uses existing `LinkInQuestion` data with updated display.

**Tech Stack:** Next.js 14, React 18, TypeScript 5, Tailwind 3.4

**Spec:** `docs/superpowers/specs/2026-03-21-ratings-ui-design.md`

---

## File Map

| Action | File | Responsibility |
|--------|------|---------------|
| Modify | `frontend/src/lib/types.ts` | Add rating types, remove vote types |
| Modify | `frontend/src/lib/api.ts` | Add rating API, remove vote API |
| Create | `frontend/src/components/ratings/rating-blocks.tsx` | Reusable R/N/G block component |
| Create | `frontend/src/components/questions/links-tab.tsx` | Links display with colored cards |
| Delete | `frontend/src/components/questions/vote-buttons.tsx` | Vote arrows component |
| Modify | `frontend/src/app/page.tsx` | Replace vote handling with rating grid |
| Modify | `frontend/src/app/questions/[id]/page.tsx` | Add ratings, links tab, remove votes |
| Modify | `frontend/src/components/feed/feed-card.tsx` | Replace vote arrows with tiny grid |
| Modify | `frontend/src/components/feed/feed-preview.tsx` | Remove score references |
| Modify | `frontend/src/components/questions/answer-card.tsx` | Replace votes with inline ratings |
| Modify | `frontend/src/components/questions/comment-list.tsx` | Remove inline vote buttons |
| Modify | `frontend/src/components/related-link-card.tsx` | Update link types |
| Modify | `frontend/src/components/questions/question-card.tsx` | Remove score display |
| Modify | `frontend/src/app/dashboard/page.tsx` | Remove score display in starter questions |
| Modify | `frontend/src/app/profile/[id]/page.tsx` | Update ActivityCard score → frontier_score |

---

## Task 1: Add Rating Types and API Functions

**Files:**
- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/lib/api.ts`

- [ ] **Step 1: Add rating types to types.ts**

Add after the existing type definitions:

```typescript
// --- Ratings ---

export interface RatingCreate {
  target_type: "question" | "answer" | "comment";
  target_id: string;
  rigour: number;
  novelty: number;
  generativity: number;
  reasoning?: string;
}

export interface RatingResponse {
  id: string;
  rater_id: string;
  rater_name: string;
  target_type: string;
  target_id: string;
  rigour: number;
  novelty: number;
  generativity: number;
  is_human: boolean;
  created_at: string;
}

export interface RatingConsensus {
  rigour: number;
  novelty: number;
  generativity: number;
}

export interface RatingsForItem {
  ratings: RatingResponse[];
  consensus: RatingConsensus;
  human_rating: RatingResponse | null;
  frontier_score: number;
}
```

Update `LinkInQuestion.link_type` to: `"references" | "extends" | "contradicts"`.
Add `reason: string | null` to `LinkInQuestion` if not already present.

Remove `ViewerVote` type and `VoteMutationResult` interface.

Also remove `score` field from `PreviewComment`, `PreviewAnswer`, `QuestionFeedPreview` if present.
Update `GraphEdge.edge_type` comment to remove `"solves" | "repost"`.
Remove `showSolves` and `showRepost` from `GraphFilterState` if present.

- [ ] **Step 2: Add rating API functions to api.ts**

Add a `ratings` export object:

```typescript
export const ratings = {
  submit: (data: RatingCreate) =>
    request<{ status: string; frontier_score: number; rigour: number; novelty: number; generativity: number }>(
      "/ratings", { method: "POST", body: JSON.stringify(data) }
    ),
  get: (targetType: string, targetId: string) =>
    request<RatingsForItem>(`/ratings?target_type=${targetType}&target_id=${targetId}`),
};
```

Remove the `votes` export object entirely.

- [ ] **Step 3: Remove vote-related fields from response types**

In `QuestionScanSummary`, `QuestionSummary`, `CommentInQuestion`, `AnswerInQuestion`: remove `upvotes`, `downvotes`, `score`, `viewer_vote` fields if they still exist in the frontend types.

Ensure `frontier_score: number` exists on `QuestionScanSummary`, `AnswerInQuestion`, and any answer response types.

- [ ] **Step 4: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: many errors (vote references in components) — that's fine, we'll fix them in later tasks.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/types.ts frontend/src/lib/api.ts
git commit -m "feat: add rating types and API, remove vote types and API"
```

---

## Task 2: Create RatingBlocks Component

**Files:**
- Create: `frontend/src/components/ratings/rating-blocks.tsx`

- [ ] **Step 1: Create the component directory**

```bash
mkdir -p frontend/src/components/ratings
```

- [ ] **Step 2: Write the RatingBlocks component**

Create `frontend/src/components/ratings/rating-blocks.tsx`. This is the core reusable component.

Props:
```typescript
interface RatingBlocksProps {
  targetType: "question" | "answer" | "comment";
  targetId: string;
  variant: "card" | "question" | "inline";
  initialConsensus?: RatingConsensus;
  initialFrontierScore?: number;
  onRated?: () => void;  // callback after successful submission
}
```

The component must:
1. Maintain local state for each axis selection: `rigour`, `novelty`, `generativity` (each `number | null`)
2. Maintain `consensus`, `frontierScore`, `hasRated`, `loading` state
3. Derive `ratingCount` from `ratings.length` in the response
4. On mount, call `ratings.get()` to check if user has rated (populates consensus if they have, empty if blind gate). Show subtle loading skeleton while fetching.
5. On click: fill blocks 1-N, set axis value. When all 3 axes are set, auto-submit via `ratings.submit()`. Show brief pulse animation during submit.
6. After submit: re-fetch ratings to get consensus. Call `onRated?.()`.
7. Hover: preview blocks 1-N in lighter shade before clicking.
8. **Update flow (State 4):** After initial submission, clicking any axis immediately re-submits with the changed value (no need to set all 3 again).
9. **Unauthenticated:** If no session cookie, render as read-only display (no hover, no click). Show consensus openly (backend returns full data for unauthenticated requests).

**Variant rendering:**
- `card`: 3 rows × 5 blocks at 8×8px. Frontier score below. No labels.
- `question`: Horizontal layout — R/N/G side by side, axis labels above, blocks 22×14px, frontier score on right, "show details" expander.
- `inline`: Horizontal compact — R[blocks] N[blocks] G[blocks] score. Blocks 14×9px.

**Color constants:**
```typescript
const AXIS_COLORS = {
  rigour: "#6b9fff",
  novelty: "#a78bfa",
  generativity: "#34d399",
} as const;
const EMPTY_BG = "#2a2a3e";
const EMPTY_BORDER = "#3a3a4e";
```

**Blind mode:** If `ratings.get()` returns empty ratings array AND user is authenticated, show empty bordered blocks with "rate to reveal" text (inline variant) or empty blocks (card variant). After user rates, re-fetch shows consensus.

**"Show details" expander (question variant only):** Below the blocks and frontier score, render a "show details" link. When clicked, expands a section showing individual raters: name, R/N/G values, is_human badge. Human ratings highlighted in green (#34d399).

**Error handling:** On submit failure, show brief inline error below blocks, preserve selections. On 401, show "log in to rate" link.

- [ ] **Step 3: Verify component renders in isolation**

Temporarily import into any page to test rendering. Verify all 3 variants render.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ratings/
git commit -m "feat: RatingBlocks component — 3 variants, blind mode, auto-submit"
```

---

## Task 3: Replace Vote Arrows on Main Feed

**Files:**
- Modify: `frontend/src/app/page.tsx` (lines 4, 75-86, 130)
- Modify: `frontend/src/components/feed/feed-card.tsx` (lines 26-32)
- Modify: `frontend/src/components/feed/feed-preview.tsx` (score references)

- [ ] **Step 1: Update feed-card.tsx — replace VoteButtons with RatingBlocks**

Remove `VoteButtons` import and the vote buttons section (lines 26-32). Replace with:

```tsx
<RatingBlocks
  targetType="question"
  targetId={summary.id}
  variant="card"
  initialFrontierScore={summary.frontier_score}
/>
```

Remove the `onVote` prop from `FeedCardProps`. Add `frontier_score` to any missing summary type fields.

- [ ] **Step 2: Update page.tsx — remove vote handling**

Remove `votes` import (line 4), `handleVote` function (lines 75-86), and `onVote={handleVote}` prop (line 130).

Remove state patches that update `viewer_vote`, `upvotes`, `downvotes` on question items.

- [ ] **Step 3: Update feed-preview.tsx — remove score references**

In `ReviewPreviewCard` and `AnswerPreviewCard` subcomponents, remove any `score` color-coding or display. Replace with `frontier_score` if available, otherwise remove.

- [ ] **Step 4: Build and test**

```bash
cd frontend && npm run build
```

Fix any TypeScript errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/page.tsx frontend/src/components/feed/
git commit -m "feat: replace vote arrows with R/N/G grid on main feed"
```

---

## Task 4: Update Question Detail Page — Ratings + Links Tab

**Files:**
- Modify: `frontend/src/app/questions/[id]/page.tsx`
- Create: `frontend/src/components/questions/links-tab.tsx`

- [ ] **Step 1: Create LinksTab component**

Create `frontend/src/components/questions/links-tab.tsx`:

```typescript
interface LinksTabProps {
  links: LinkInQuestion[];
}
```

Renders link cards with:
- Left border color: extends=#f59e0b, contradicts=#ef4444, references=#888
- Link type label (uppercase, colored)
- Created by + timestamp
- Target question title as hyperlink (uses `relatedHref()` pattern from `related-link-card.tsx`)
- Reason in grey box (for extends/contradicts)
- Community badge

- [ ] **Step 2: Add tab switcher to question detail page**

In `page.tsx`, add state: `const [activeTab, setActiveTab] = useState<"problem" | "links">("problem")`

Above the problem body, render tab bar:
```tsx
<div className="flex gap-4 border-b border-gray-800 mb-3">
  <button
    onClick={() => setActiveTab("problem")}
    className={activeTab === "problem" ? "text-white border-b-2 border-blue-400 pb-2" : "text-gray-500 pb-2"}
  >Problem</button>
  <button
    onClick={() => setActiveTab("links")}
    className={activeTab === "links" ? "text-white border-b-2 border-blue-400 pb-2" : "text-gray-500 pb-2"}
  >Links <span className="bg-gray-800 text-gray-400 text-xs px-1.5 rounded-full ml-1">{question.related.length}</span></button>
</div>
```

Conditionally render problem body or LinksTab based on `activeTab`.

- [ ] **Step 3: Replace vote arrows with RatingBlocks on question**

Remove `VoteButtons` from the problem section (line 159). Remove `handleQuestionVote` function (lines 55-68).

Add `RatingBlocks variant="question"` below the problem body (before Problem Reviews section):

```tsx
<RatingBlocks
  targetType="question"
  targetId={question.id}
  variant="question"
  initialFrontierScore={question.frontier_score}
/>
```

- [ ] **Step 4: Remove vote imports and handlers**

Remove `votes` import from api. Remove `handleQuestionVote`, `handleAnswerVote`, `handleCommentVote` functions. Remove all vote-related state patches.

- [ ] **Step 5: Build and test**

```bash
cd frontend && npm run build
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/app/questions/ frontend/src/components/questions/links-tab.tsx
git commit -m "feat: question detail — ratings below body, links tab, remove votes"
```

---

## Task 5: Update Answer Cards and Comment List

**Files:**
- Modify: `frontend/src/components/questions/answer-card.tsx` (lines 28-35)
- Modify: `frontend/src/components/questions/comment-list.tsx` (lines 72-91)

- [ ] **Step 1: Replace vote arrows on answer cards**

In `answer-card.tsx`, remove `VoteButtons` import and usage (lines 28-35). Replace with `RatingBlocks variant="inline"` below the answer body, above the comments:

```tsx
<div className="border-t border-gray-800 pt-2 mt-2">
  <RatingBlocks
    targetType="answer"
    targetId={answer.id}
    variant="inline"
    initialFrontierScore={answer.frontier_score}
  />
</div>
```

Remove `onVoteAnswer` prop. Remove vote-related props entirely.

- [ ] **Step 2: Remove inline vote buttons from comment list**

In `comment-list.tsx`, remove the inline upvote/downvote buttons in `CommentItem` (lines 72-91). Remove `score` display. Keep verdict badge, author, body, timestamp.

Remove `onVoteComment` prop from `CommentList` and `CommentItem`.

- [ ] **Step 3: Update related-link-card.tsx**

Update link type display: change `"Repost"` to `"References"` and `"Reference"` to `"References"`. Remove `"Solves"`. This component is used for inline link previews in the problem body — the new LinksTab handles the full display.

- [ ] **Step 4: Build and test**

```bash
cd frontend && npm run build
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/questions/ frontend/src/components/related-link-card.tsx
git commit -m "feat: inline ratings on answers, remove vote buttons from comments"
```

---

## Task 6: Delete Vote Component and Clean Up

**Files:**
- Delete: `frontend/src/components/questions/vote-buttons.tsx`
- Modify: any remaining files with vote imports

- [ ] **Step 1: Delete vote-buttons.tsx**

```bash
rm frontend/src/components/questions/vote-buttons.tsx
```

- [ ] **Step 2: Search for remaining vote references**

```bash
grep -r "vote\|Vote\|upvote\|downvote\|viewer_vote" frontend/src/ --include="*.tsx" --include="*.ts" | grep -v node_modules | grep -v ".next"
```

Fix any remaining references. Known files to check:
- `frontend/src/components/questions/question-card.tsx` — remove `score` display
- `frontend/src/app/dashboard/page.tsx` — remove `score` in starter questions section (~line 577)
- `frontend/src/app/profile/[id]/page.tsx` — update `ActivityCard` to use `frontier_score` instead of `score` (~line 242)
- Import statements referencing deleted VoteButtons component
- Props that pass vote handlers
- State updates that patch vote fields

- [ ] **Step 3: Full build**

```bash
cd frontend && npm run build
```

Must succeed with zero errors.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: delete vote-buttons component, clean up all vote references"
```

---

## Task 7: Deploy and Verify

- [ ] **Step 1: Push and deploy**

```bash
git push origin feature/v2-backend-restructure
ssh morgansclawdbot "cd ~/Assay && git fetch origin && git merge origin/feature/v2-backend-restructure --no-edit && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build web"
```

- [ ] **Step 2: Verify on assayz.uk**

1. Main feed: vote arrows gone, tiny R/N/G grid on each card
2. Question detail: tab switcher (Problem | Links), rating blocks below body
3. Click R=4, N=3, G=5 on a question → auto-submits, consensus appears
4. Click "show details" → individual raters expand
5. Change one axis → re-submits immediately with updated value
6. Answer cards: inline rating blocks between body and reviews
7. Comments: no vote buttons, verdicts still shown
8. Links tab: colored cards with reasons and hyperlinked targets
9. Click a linked question title → navigates to that question
10. Open question while logged out → consensus visible, blocks not interactive
11. Dashboard page: no score references
12. Profile page: frontier_score instead of score
13. Analytics/graph page: still renders correctly

- [ ] **Step 3: Commit any fixes**

---

## Implementation Order

```
Task 1 (Types + API)         ← START HERE
  ↓
Task 2 (RatingBlocks)        ← depends on Task 1
  ↓
Task 3 (Main feed)           ← depends on Task 2
Task 4 (Question detail)     ← depends on Task 2, can parallel with Task 3
Task 5 (Answers + comments)  ← depends on Task 2, can parallel with Task 3-4
  ↓
Task 6 (Cleanup)             ← depends on Tasks 3-5
  ↓
Task 7 (Deploy)              ← depends on Task 6
```

Tasks 3, 4, 5 can be parallelised across subagents.
