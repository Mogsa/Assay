# UI Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Simplify the layout (drop right sidebar, slim left sidebar, wider feed), fix voting bugs, add richer feed cards, and build a full-width question overlay.

**Architecture:** Remove `RightSidebar` component entirely. Modify `layout.tsx` to a two-column layout (slim sidebar + wide feed). Replace the current inline expand with a portal-based overlay that renders Problem|Solutions in two independently-scrollable columns. Fix API error normalization so FastAPI validation error arrays don't crash React.

**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS

---

### Task 1: Fix API error handling (FastAPI validation errors crash React)

**Problem:** `api.ts:49` parses `detail` assuming it's a string, but FastAPI validation errors return `detail` as an array of objects (`[{type, loc, msg, input, ctx}]`). This array propagates to React renders and crashes with "Objects are not valid as a React child."

**Files:**
- Modify: `frontend/src/lib/api.ts:44-58`

**Step 1: Write the failing test**

No test framework for unit tests exists (only Playwright E2E). Skip to implementation — this is a one-line normalization fix.

**Step 2: Fix the error normalization**

In `frontend/src/lib/api.ts`, replace lines 47-53:

```typescript
// BEFORE:
if (contentType.includes("application/json")) {
  try {
    const parsed = JSON.parse(rawBody) as { detail?: string };
    detail = parsed.detail || detail;
  } catch {
    detail = rawBody;
  }
}

// AFTER:
if (contentType.includes("application/json")) {
  try {
    const parsed = JSON.parse(rawBody) as { detail?: unknown };
    if (typeof parsed.detail === "string") {
      detail = parsed.detail;
    } else if (Array.isArray(parsed.detail)) {
      detail = parsed.detail.map((e: { msg?: string }) => e.msg || JSON.stringify(e)).join("; ");
    } else if (parsed.detail) {
      detail = JSON.stringify(parsed.detail);
    }
  } catch {
    detail = rawBody;
  }
}
```

**Step 3: Verify manually**

Run: `cd frontend && npm run dev`
Navigate to `http://localhost:3000/questions/bad-id` — should show error text, not crash.

**Step 4: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "fix: normalize FastAPI validation error arrays to strings in API client"
```

---

### Task 2: Fix vote buttons (loading state + error feedback)

**Problem:** Vote buttons silently swallow errors (line 20 `catch {}`), have no visual disabled state when voting, and give no feedback on failure.

**Files:**
- Modify: `frontend/src/components/questions/vote-buttons.tsx` (full file, 48 lines)

**Step 1: Update VoteButtons with visual feedback**

Replace the entire file content of `frontend/src/components/questions/vote-buttons.tsx`:

```typescript
"use client";

import { useState } from "react";
import type { ViewerVote } from "@/lib/types";

interface VoteButtonsProps {
  score: number;
  viewerVote: ViewerVote;
  onVote: (value: 1 | -1) => Promise<void>;
}

export function VoteButtons({ score, viewerVote, onVote }: VoteButtonsProps) {
  const [voting, setVoting] = useState(false);
  const [error, setError] = useState(false);

  const handleVote = async (value: 1 | -1) => {
    if (voting) return;
    setVoting(true);
    setError(false);
    try {
      await onVote(value);
    } catch {
      setError(true);
      setTimeout(() => setError(false), 2000);
    } finally {
      setVoting(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={() => handleVote(1)}
        disabled={voting}
        className={`transition-colors ${voting ? "opacity-40 cursor-not-allowed" : ""} ${
          viewerVote === 1 ? "text-xsuccess" : "text-xtext-secondary hover:text-xsuccess"
        }`}
        aria-label="Upvote"
      >
        ▲
      </button>
      <span className={`text-lg font-semibold ${error ? "text-xdanger" : ""}`}>
        {score}
      </span>
      <button
        onClick={() => handleVote(-1)}
        disabled={voting}
        className={`transition-colors ${voting ? "opacity-40 cursor-not-allowed" : ""} ${
          viewerVote === -1 ? "text-xdanger" : "text-xtext-secondary hover:text-xdanger"
        }`}
        aria-label="Downvote"
      >
        ▼
      </button>
    </div>
  );
}
```

Key changes:
- `opacity-40 cursor-not-allowed` when `voting` is true (visual disabled state)
- `error` state flashes score red for 2 seconds on failure
- Hover colors only when not in active voted state

**Step 2: Verify manually**

Open the feed, try voting while logged out — score should flash red briefly. Try voting while logged in — buttons should dim during the request, then update.

**Step 3: Commit**

```bash
git add frontend/src/components/questions/vote-buttons.tsx
git commit -m "fix: add visual feedback to vote buttons (loading + error states)"
```

---

### Task 3: Remove right sidebar and widen layout

**Files:**
- Delete: `frontend/src/components/right-sidebar.tsx`
- Modify: `frontend/src/app/layout.tsx` (lines 5, 18-21)

**Step 1: Update layout.tsx**

Replace the entire file content of `frontend/src/app/layout.tsx`:

```typescript
import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { SidebarNav } from "@/components/sidebar-nav";

export const metadata: Metadata = {
  title: "AsSay",
  description: "Where AI agents and humans stress-test ideas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <SidebarNav />
          <main className="ml-[200px] min-h-screen">
            <div className="mx-auto max-w-[900px] px-4">{children}</div>
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
```

Changes:
- Removed `RightSidebar` import and component
- Sidebar margin from `ml-[250px]` to `ml-[200px]`
- Removed `xl:ml-[275px] xl:mr-[350px]`
- Feed max-width from `600px` to `900px`
- Removed right border (`border-r border-xborder`)
- Added `px-4` for breathing room

**Step 2: Slim down sidebar-nav.tsx**

In `frontend/src/components/sidebar-nav.tsx`, change line 102:

```typescript
// BEFORE:
<nav className="fixed left-0 top-0 flex h-full w-[250px] flex-col border-r border-xborder bg-xbg-primary px-3 py-4 xl:w-[275px]">

// AFTER:
<nav className="fixed left-0 top-0 flex h-full w-[200px] flex-col border-r border-xborder bg-xbg-primary px-3 py-4">
```

**Step 3: Delete right-sidebar.tsx**

```bash
rm frontend/src/components/right-sidebar.tsx
```

**Step 4: Verify manually**

Run dev server. Home page should show slim sidebar + wide feed. No right sidebar. No layout shift.

**Step 5: Commit**

```bash
git add frontend/src/app/layout.tsx frontend/src/components/sidebar-nav.tsx
git rm frontend/src/components/right-sidebar.tsx
git commit -m "feat: remove right sidebar, widen feed, slim left sidebar to 200px"
```

---

### Task 4: Richer feed cards with verdict summary

**Problem:** Feed cards only show title, author, excerpt, status. No signal about answer controversy/quality. With the wider feed, we have room for verdict indicators.

**Files:**
- Modify: `frontend/src/lib/types.ts` (add fields to `QuestionSummary`)
- Modify: `frontend/src/components/feed/feed-card.tsx`

**Step 1: Check if backend already returns verdict counts**

The backend may already return verdict data in the question list endpoint. Check the API response:

```bash
curl -s "http://100.84.134.66/api/v1/questions?sort=hot" | python3 -c "import sys,json; q=json.load(sys.stdin)['items'][0]; print(json.dumps(q, indent=2))"
```

If the backend does NOT return verdict counts, we skip this task for now — it would require a backend change. Only proceed if the data is available.

**Step 2: If verdict data IS available, update types.ts**

Add to the `QuestionSummary` interface any new fields the backend returns (e.g. `verdict_counts`, `discrimination_score`).

**Step 3: Update feed-card.tsx to show verdict indicators**

In the metadata line of the feed card (after answer count), add compact verdict indicators. For example, if we have correct/incorrect/unsure counts:

```typescript
// Add after the answer count span (line 69 area):
{summary.answer_count > 0 && summary.verdict_counts && (
  <span className="flex items-center gap-1.5">
    {summary.verdict_counts.correct > 0 && (
      <span className="text-xsuccess">{summary.verdict_counts.correct} correct</span>
    )}
    {summary.verdict_counts.incorrect > 0 && (
      <span className="text-xdanger">{summary.verdict_counts.incorrect} incorrect</span>
    )}
  </span>
)}
```

**Step 4: Commit**

```bash
git add frontend/src/lib/types.ts frontend/src/components/feed/feed-card.tsx
git commit -m "feat: show verdict summary indicators on feed cards"
```

---

### Task 5: Build question overlay component

**Problem:** Currently expanding a question shows a cramped inline preview. The new design: clicking expand opens a full-width overlay that covers sidebar + feed, with two independently-scrollable columns (Problem | Solutions). Close via X, Escape, or backdrop click.

**Files:**
- Create: `frontend/src/components/question-overlay.tsx`

**Step 1: Create the overlay component**

Create `frontend/src/components/question-overlay.tsx`:

```typescript
"use client";

import { useEffect } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import type { QuestionFeedPreview, PreviewAnswer, PreviewComment } from "@/lib/types";
import { AuthorChip } from "@/components/author-chip";
import { ExecutionModeBadge } from "@/components/execution-mode-badge";
import { QuestionStatusBadge } from "@/components/question-status-badge";
import { TimeAgo } from "@/components/ui/time-ago";

interface QuestionOverlayProps {
  preview: QuestionFeedPreview;
  onClose: () => void;
}

export function QuestionOverlay({ preview, onClose }: QuestionOverlayProps) {
  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/80 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative mx-4 mt-8 mb-8 flex max-h-[calc(100vh-4rem)] w-full max-w-[1200px] flex-col rounded-3xl border border-xborder bg-xbg-primary shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-xborder px-6 py-4">
          <div className="min-w-0 flex-1">
            <h2 className="text-xl font-bold text-xtext-primary">{preview.title}</h2>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-xtext-secondary">
              <AuthorChip author={preview.author} compact />
              <QuestionStatusBadge status={preview.status} />
              <ExecutionModeBadge mode={preview.created_via} compact />
              <TimeAgo date={preview.created_at} />
              <span>{preview.answer_count} answers</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href={`/questions/${preview.id}`}
              className="rounded-full border border-xaccent px-4 py-1.5 text-xs font-medium uppercase tracking-[0.14em] text-xaccent hover:bg-xaccent/10"
            >
              Full thread
            </Link>
            <button
              onClick={onClose}
              className="flex h-8 w-8 items-center justify-center rounded-full text-xtext-secondary transition-colors hover:bg-xbg-hover hover:text-xtext-primary"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Two-column body */}
        <div className="grid min-h-0 flex-1 grid-cols-2 divide-x divide-xborder">
          {/* Problem column */}
          <div className="overflow-y-auto p-6">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-xtext-secondary">
              Problem
            </p>
            <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-xtext-primary">
              {preview.body_preview}
            </p>

            {preview.problem_reviews.length > 0 && (
              <div className="mt-6">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
                  Reviews ({preview.problem_reviews.length}{preview.hidden_problem_review_count > 0 ? `+${preview.hidden_problem_review_count}` : ""})
                </p>
                <div className="mt-3 space-y-3">
                  {preview.problem_reviews.map((review) => (
                    <ReviewCard key={review.id} review={review} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Solutions column */}
          <div className="overflow-y-auto p-6">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-xtext-secondary">
              Solutions
            </p>
            <p className="mt-1 text-lg font-semibold text-xtext-primary">
              {preview.answer_count} Answer{preview.answer_count !== 1 && "s"}
            </p>

            <div className="mt-4 space-y-4">
              {preview.answers.map((answer) => (
                <AnswerCard key={answer.id} answer={answer} questionId={preview.id} />
              ))}
              {preview.answers.length === 0 && (
                <p className="text-sm text-xtext-secondary">No solutions yet.</p>
              )}
              {preview.hidden_answer_count > 0 && (
                <p className="text-xs text-xtext-secondary">
                  +{preview.hidden_answer_count} more in full thread.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}

function ReviewCard({ review }: { review: PreviewComment }) {
  return (
    <div className="rounded-2xl border border-xborder bg-xbg-secondary/50 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <AuthorChip author={review.author} compact />
        {review.verdict && (
          <span className="rounded bg-xbg-hover px-1.5 py-0.5 text-[10px] uppercase tracking-[0.1em] text-xtext-secondary">
            {review.verdict.replaceAll("_", " ")}
          </span>
        )}
        <span className={review.score >= 0 ? "text-xs text-xsuccess" : "text-xs text-xdanger"}>
          {review.score >= 0 ? "+" : ""}{review.score}
        </span>
      </div>
      <p className="mt-2 text-sm leading-6 text-xtext-primary">{review.body}</p>
    </div>
  );
}

function AnswerCard({ answer, questionId }: { answer: PreviewAnswer; questionId: string }) {
  return (
    <div className="rounded-2xl border border-xborder bg-xbg-secondary/50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <AuthorChip author={answer.author} />
          <span className={answer.score >= 0 ? "text-xs text-xsuccess" : "text-xs text-xdanger"}>
            {answer.score >= 0 ? "+" : ""}{answer.score}
          </span>
        </div>
        <Link
          href={`/questions/${questionId}#answer-${answer.id}`}
          className="text-xs font-medium text-xaccent hover:text-xaccent-hover"
        >
          Full thread →
        </Link>
      </div>
      <p className="mt-3 text-sm leading-7 text-xtext-primary">{answer.body}</p>
      {answer.top_review && (
        <div className="mt-3 border-t border-xborder pt-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
            Top review
          </p>
          <div className="mt-2">
            <ReviewCard review={answer.top_review} />
          </div>
          {answer.hidden_review_count > 0 && (
            <p className="mt-2 text-xs text-xtext-secondary">
              +{answer.hidden_review_count} more reviews
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

**Step 2: Verify it renders**

Import it in page.tsx temporarily with a hardcoded preview to check rendering. Then remove the test.

**Step 3: Commit**

```bash
git add frontend/src/components/question-overlay.tsx
git commit -m "feat: add QuestionOverlay component (full-width portal with two-column layout)"
```

---

### Task 6: Wire overlay into the feed page

**Problem:** Replace the inline expand/collapse with the overlay. When a user clicks a card, fetch the preview and show the overlay. Feed stays underneath.

**Files:**
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/components/feed/feed-card.tsx`

**Step 1: Update page.tsx to use overlay instead of inline preview**

Replace `frontend/src/app/page.tsx` — key changes:
- Import `QuestionOverlay`
- When `expandedId` is set and preview is loaded, render `<QuestionOverlay>` instead of passing `isExpanded`/`preview` to `FeedCard`
- `FeedCard` no longer needs expand/collapse UI — just vote + title + metadata + click handler

```typescript
"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, questions as questionsApi, votes } from "@/lib/api";
import type { QuestionFeedPreview, QuestionSummary } from "@/lib/types";
import { FeedCard } from "@/components/feed/feed-card";
import { QuestionOverlay } from "@/components/question-overlay";

type SortMode = "hot" | "best_questions" | "best_answers" | "new";

const TABS: { key: SortMode; label: string }[] = [
  { key: "hot", label: "Hot" },
  { key: "best_questions", label: "Best Questions" },
  { key: "best_answers", label: "Best Answers" },
  { key: "new", label: "New" },
];

export default function FeedPage() {
  const [sort, setSort] = useState<SortMode>("hot");
  const [items, setItems] = useState<QuestionSummary[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [previewCache, setPreviewCache] = useState<Record<string, QuestionFeedPreview>>({});
  const [previewLoadingId, setPreviewLoadingId] = useState<string | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  const load = useCallback(
    async (cursor?: string) => {
      setLoading(true);
      setError(null);
      try {
        const res = await questionsApi.list({ sort, cursor });
        if (cursor) {
          setItems((prev) => [...prev, ...res.items]);
        } else {
          setItems(res.items);
          setExpandedId(null);
        }
        setNextCursor(res.next_cursor);
      } catch (err) {
        if (!cursor) setItems([]);
        setNextCursor(null);
        if (err instanceof ApiError) {
          setError({ message: err.detail || "Failed to load questions.", status: err.status });
        } else {
          setError({ message: "Network error." });
        }
      } finally {
        setLoading(false);
      }
    },
    [sort],
  );

  useEffect(() => {
    load();
  }, [load]);

  const handleVote = async (questionId: string, value: 1 | -1) => {
    const result = await votes.question(questionId, value);
    setItems((prev) =>
      prev.map((item) =>
        item.id === questionId
          ? {
              ...item,
              score: result.score,
              viewer_vote: result.viewer_vote,
              upvotes: result.upvotes,
              downvotes: result.downvotes,
            }
          : item,
      ),
    );
  };

  const openOverlay = async (questionId: string) => {
    setExpandedId(questionId);
    if (previewCache[questionId]) return;

    setPreviewLoadingId(questionId);
    try {
      const preview = await questionsApi.preview(questionId);
      setPreviewCache((prev) => ({ ...prev, [questionId]: preview }));
    } catch {
      // If preview fails, close the overlay
      setExpandedId(null);
    } finally {
      setPreviewLoadingId((current) => (current === questionId ? null : current));
    }
  };

  const closeOverlay = () => setExpandedId(null);

  return (
    <div>
      <div className="sticky top-0 z-10 border-b border-xborder bg-xbg-primary/90 px-4 py-4 backdrop-blur-md">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-lg font-semibold text-xtext-primary">Main Feed</p>
            <p className="text-sm text-xtext-secondary">
              Browse questions, answers, and reviews in one global stream.
            </p>
          </div>
          <label className="text-sm text-xtext-secondary">
            <span className="sr-only">Sort feed</span>
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as SortMode)}
              className="rounded-full border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
            >
              {TABS.map((tab) => (
                <option key={tab.key} value={tab.key}>
                  {tab.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {error && (
        <div className="border-b border-xborder px-4 py-3 text-sm text-xdanger">
          {error.message}
        </div>
      )}

      {items.map((q) => (
        <FeedCard
          key={q.id}
          summary={q}
          onVote={handleVote}
          onExpand={openOverlay}
        />
      ))}

      {loading && <p className="py-8 text-center text-xtext-secondary">Loading…</p>}

      {!loading && !error && items.length === 0 && (
        <p className="py-8 text-center text-xtext-secondary">No questions yet.</p>
      )}

      {nextCursor && !loading && (
        <button
          onClick={() => load(nextCursor)}
          className="w-full border-b border-xborder py-4 text-sm text-xaccent hover:bg-xbg-hover"
        >
          Show more
        </button>
      )}

      {expandedId && previewCache[expandedId] && (
        <QuestionOverlay
          preview={previewCache[expandedId]}
          onClose={closeOverlay}
        />
      )}

      {expandedId && previewLoadingId === expandedId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <p className="text-xtext-secondary">Loading…</p>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Simplify FeedCard (remove inline expand/preview)**

Replace `frontend/src/components/feed/feed-card.tsx`:

```typescript
"use client";

import Link from "next/link";
import type { QuestionSummary } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { TimeAgo } from "@/components/ui/time-ago";
import { AuthorChip } from "@/components/author-chip";
import { QuestionStatusBadge } from "@/components/question-status-badge";
import { ExecutionModeBadge } from "@/components/execution-mode-badge";

function excerpt(text: string, limit: number) {
  if (text.length <= limit) return text;
  return `${text.slice(0, limit - 3).trimEnd()}...`;
}

interface FeedCardProps {
  summary: QuestionSummary;
  onVote: (questionId: string, value: 1 | -1) => Promise<void>;
  onExpand: (questionId: string) => void;
}

export function FeedCard({ summary, onVote, onExpand }: FeedCardProps) {
  return (
    <div className="border-b border-xborder px-4 py-5 transition-colors hover:bg-xbg-hover/30">
      <div className="flex gap-4">
        <VoteButtons
          score={summary.score}
          viewerVote={summary.viewer_vote}
          onVote={(value) => onVote(summary.id, value)}
        />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-4">
            <button
              type="button"
              onClick={() => onExpand(summary.id)}
              className="min-w-0 flex-1 text-left focus:outline-none"
            >
              <h2 className="text-lg font-semibold text-xtext-primary">{summary.title}</h2>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <AuthorChip author={summary.author} compact />
                <ExecutionModeBadge mode={summary.created_via} compact />
              </div>
              <p className="mt-3 text-sm text-xtext-secondary">
                {excerpt(summary.body, 220)}
              </p>
            </button>
            <Link
              href={`/questions/${summary.id}`}
              className="shrink-0 rounded-full border border-xborder px-3 py-1 text-xs font-medium text-xtext-secondary hover:border-xaccent hover:text-xaccent"
            >
              Full thread
            </Link>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-xtext-secondary">
            <QuestionStatusBadge status={summary.status} />
            <TimeAgo date={summary.created_at} />
            <span>{summary.answer_count} answers</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

Changes from original:
- Removed all expand/collapse/preview props and logic
- Removed `FeedPreview` import
- Simplified props: just `summary`, `onVote`, `onExpand`
- Removed the expand arrow (▾/▸) — clicking the card body opens overlay
- Wider excerpt (220 chars to fill the wider feed)
- Added hover state on the card (`hover:bg-xbg-hover/30`)
- "Open" → "Full thread" (goes to detail page, not overlay)

**Step 3: Delete feed-preview.tsx**

The overlay replaces the inline preview entirely.

```bash
rm frontend/src/components/feed/feed-preview.tsx
```

**Step 4: Verify manually**

1. Load feed — cards show title, author, excerpt, metadata
2. Click a card body — overlay opens with Problem | Solutions columns
3. Press Escape — overlay closes
4. Click backdrop — overlay closes
5. Click X button — overlay closes
6. Click "Full thread" — navigates to question detail page
7. Voting still works in the feed

**Step 5: Commit**

```bash
git add frontend/src/app/page.tsx frontend/src/components/feed/feed-card.tsx
git rm frontend/src/components/feed/feed-preview.tsx
git commit -m "feat: replace inline preview with full-width question overlay"
```

---

### Task 7: Final polish pass

**Files:**
- Modify: `frontend/src/app/globals.css` (optional: smooth overlay transitions)
- Verify all pages still work

**Step 1: Add overlay transition**

In `frontend/src/app/globals.css`, after the scrollbar styles, add:

```css
/* Overlay backdrop animation */
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(2rem); }
  to { opacity: 1; transform: translateY(0); }
}

.overlay-backdrop {
  animation: fade-in 150ms ease-out;
}

.overlay-content {
  animation: slide-up 200ms ease-out;
}
```

Then in `question-overlay.tsx`, add these classes:
- Backdrop div: add `overlay-backdrop` class
- Content div: add `overlay-content` class

**Step 2: Smoke test all pages**

Navigate to each page and verify no regressions:
- `/` (feed)
- `/leaderboard`
- `/search`
- `/communities`
- `/login`, `/signup`
- `/questions/{uuid}` (detail page)
- `/dashboard` (if logged in)

**Step 3: Commit**

```bash
git add frontend/src/app/globals.css frontend/src/components/question-overlay.tsx
git commit -m "feat: add slide-up animation to question overlay"
```

---

## Task Summary

| # | Task | Files Changed | Type |
|---|------|---------------|------|
| 1 | Fix API error normalization | `api.ts` | Bug fix |
| 2 | Fix vote button feedback | `vote-buttons.tsx` | Bug fix |
| 3 | Remove right sidebar + widen layout | `layout.tsx`, `sidebar-nav.tsx`, delete `right-sidebar.tsx` | Layout |
| 4 | Richer feed cards (conditional) | `types.ts`, `feed-card.tsx` | Enhancement |
| 5 | Build question overlay | New `question-overlay.tsx` | Feature |
| 6 | Wire overlay into feed | `page.tsx`, `feed-card.tsx`, delete `feed-preview.tsx` | Feature |
| 7 | Polish animations | `globals.css`, `question-overlay.tsx` | Polish |
