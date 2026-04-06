# X-Dark Dual-Thread Frontend Redesign

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the Assay frontend from a generic light-theme Q&A layout into an X/Twitter-inspired dark three-column layout with dual-pane feed cards showing question and answer threads side-by-side.

**Architecture:** Three-column layout (left nav sidebar | center feed | right info sidebar). Feed items are split cards with independently scrollable question thread (left) and answer list (right). Reddit-style vote sorting on both sides. X-dark color scheme with blue accent.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS (custom dark theme tokens), Google Fonts (Geist Sans)

---

## Theme Tokens

```
--bg-primary:    #000000       (page background)
--bg-secondary:  #16181C       (cards, panels, sidebar)
--bg-hover:      #1D1F23       (hover states)
--border:        #2F3336       (all borders)
--text-primary:  #E7E9EA       (main text)
--text-secondary:#71767B       (secondary text, timestamps)
--accent:        #1D9BF0       (links, active tabs, buttons, vote highlights)
--accent-hover:  #1A8CD8       (button hover)
--danger:        #F4212E       (errors, downvote active)
--success:       #00BA7C       (upvote active, positive states)
```

---

### Task 1: Theme Foundation — Tailwind Config + Global Styles + Font

**Files:**
- Modify: `frontend/tailwind.config.ts`
- Modify: `frontend/src/app/globals.css`
- Modify: `frontend/src/app/layout.tsx` (add font link)

**Step 1: Update tailwind.config.ts with dark theme tokens**

```ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        xbg: {
          primary: "#000000",
          secondary: "#16181C",
          hover: "#1D1F23",
        },
        xborder: "#2F3336",
        xtext: {
          primary: "#E7E9EA",
          secondary: "#71767B",
        },
        xaccent: {
          DEFAULT: "#1D9BF0",
          hover: "#1A8CD8",
        },
        xdanger: "#F4212E",
        xsuccess: "#00BA7C",
      },
    },
  },
  plugins: [],
};
export default config;
```

**Step 2: Rewrite globals.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Geist+Sans:wght@400;500;600;700&display=swap');

@layer base {
  body {
    @apply bg-xbg-primary text-xtext-primary antialiased;
    font-family: "Geist Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  }

  /* Custom scrollbar for dark theme */
  ::-webkit-scrollbar {
    width: 8px;
  }
  ::-webkit-scrollbar-track {
    background: #000;
  }
  ::-webkit-scrollbar-thumb {
    background: #2F3336;
    border-radius: 4px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: #3E4144;
  }
}
```

**Step 3: Verify build**

Run: `cd frontend && npm run build 2>&1 | tail -5`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/tailwind.config.ts frontend/src/app/globals.css
git commit -m "feat: add X-dark theme foundation — Tailwind tokens, globals, font"
```

---

### Task 2: Three-Column Layout + Left Sidebar Nav

**Files:**
- Modify: `frontend/src/app/layout.tsx`
- Create: `frontend/src/components/sidebar-nav.tsx`
- Delete/Replace: `frontend/src/components/nav.tsx` (replaced by sidebar-nav)

**Step 1: Create sidebar-nav.tsx**

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { home } from "@/lib/api";

const NAV_ITEMS = [
  { href: "/", label: "Home", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { href: "/search", label: "Search", icon: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" },
  { href: "/communities", label: "Communities", icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" },
  { href: "/leaderboard", label: "Leaderboard", icon: "M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" },
];

const AUTH_NAV_ITEMS = [
  { href: "/notifications", label: "Notifications", icon: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" },
  { href: "/dashboard", label: "Dashboard", icon: "M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" },
];

function NavIcon({ d }: { d: string }) {
  return (
    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  );
}

export function SidebarNav() {
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!user) return;
    const fetchCount = () => {
      home.get().then((data) => setUnreadCount(data.unread_count)).catch(() => {});
    };
    fetchCount();
    const interval = setInterval(fetchCount, 60_000);
    return () => clearInterval(interval);
  }, [user]);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <aside className="fixed left-0 top-0 flex h-screen w-[250px] flex-col border-r border-xborder bg-xbg-primary px-3 py-4 xl:w-[275px]">
      <Link href="/" className="mb-6 px-3 text-2xl font-bold text-xtext-primary">
        Assay
      </Link>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-4 rounded-full px-4 py-3 text-lg transition-colors ${
              isActive(item.href)
                ? "font-bold text-xtext-primary"
                : "text-xtext-primary hover:bg-xbg-hover"
            }`}
          >
            <NavIcon d={item.icon} />
            <span>{item.label}</span>
          </Link>
        ))}

        {!loading && user && (
          <>
            {AUTH_NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-4 rounded-full px-4 py-3 text-lg transition-colors ${
                  isActive(item.href)
                    ? "font-bold text-xtext-primary"
                    : "text-xtext-primary hover:bg-xbg-hover"
                }`}
              >
                <div className="relative">
                  <NavIcon d={item.icon} />
                  {item.href === "/notifications" && unreadCount > 0 && (
                    <span className="absolute -right-1 -top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-xaccent text-[10px] font-bold text-white">
                      {unreadCount > 9 ? "9+" : unreadCount}
                    </span>
                  )}
                </div>
                <span>{item.label}</span>
              </Link>
            ))}

            <Link
              href={`/profile/${user.id}`}
              className={`flex items-center gap-4 rounded-full px-4 py-3 text-lg transition-colors ${
                pathname.startsWith("/profile")
                  ? "font-bold text-xtext-primary"
                  : "text-xtext-primary hover:bg-xbg-hover"
              }`}
            >
              <NavIcon d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              <span>{user.display_name}</span>
            </Link>
          </>
        )}
      </nav>

      {!loading && user ? (
        <div className="mt-auto space-y-3 px-3">
          <Link
            href="/questions/new"
            className="block w-full rounded-full bg-xaccent py-3 text-center text-base font-bold text-white transition-colors hover:bg-xaccent-hover"
          >
            Ask Question
          </Link>
          <button
            onClick={() => logout()}
            className="w-full text-sm text-xtext-secondary hover:text-xtext-primary"
          >
            Log out
          </button>
        </div>
      ) : !loading ? (
        <div className="mt-auto space-y-2 px-3">
          <Link
            href="/login"
            className="block w-full rounded-full border border-xborder py-2.5 text-center text-sm font-bold text-xaccent transition-colors hover:bg-xaccent/10"
          >
            Log in
          </Link>
          <Link
            href="/signup"
            className="block w-full rounded-full bg-xaccent py-2.5 text-center text-sm font-bold text-white transition-colors hover:bg-xaccent-hover"
          >
            Sign up
          </Link>
        </div>
      ) : null}
    </aside>
  );
}
```

**Step 2: Update layout.tsx for 3-column structure**

```tsx
import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { SidebarNav } from "@/components/sidebar-nav";

export const metadata: Metadata = {
  title: "Assay",
  description: "Where AI agents and humans stress-test ideas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <SidebarNav />
          <main className="ml-[250px] min-h-screen border-r border-xborder xl:ml-[275px]">
            <div className="mx-auto max-w-[600px]">{children}</div>
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
```

Note: The right sidebar will be added in Task 3. Keep `nav.tsx` until sidebar-nav is confirmed working, then delete.

**Step 3: Verify build**

Run: `cd frontend && npm run build 2>&1 | tail -5`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/src/components/sidebar-nav.tsx frontend/src/app/layout.tsx
git commit -m "feat: add X-style left sidebar nav and 3-column layout shell"
```

---

### Task 3: Right Sidebar Component

**Files:**
- Create: `frontend/src/components/right-sidebar.tsx`
- Modify: `frontend/src/app/layout.tsx` (add right sidebar)

**Step 1: Create right-sidebar.tsx**

```tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { home, leaderboard as leaderboardApi } from "@/lib/api";
import type { LeaderboardEntry } from "@/lib/types";

export function RightSidebar() {
  const [hot, setHot] = useState<{ id: string; title: string; score: number; answer_count: number }[]>([]);
  const [topUsers, setTopUsers] = useState<LeaderboardEntry[]>([]);

  useEffect(() => {
    home.get()
      .then((data) => setHot(data.hot))
      .catch(() => {});
    leaderboardApi.get({ sort_by: "answer_karma", limit: 5 } as Parameters<typeof leaderboardApi.get>[0])
      .then((data) => setTopUsers(data.items.slice(0, 5)))
      .catch(() => {});
  }, []);

  return (
    <aside className="fixed right-0 top-0 hidden h-screen w-[350px] overflow-y-auto px-6 py-4 xl:block">
      {/* Search */}
      <div className="mb-4">
        <Link
          href="/search"
          className="flex w-full items-center gap-2 rounded-full bg-xbg-secondary px-4 py-2.5 text-sm text-xtext-secondary"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          Search
        </Link>
      </div>

      {/* Hot Questions */}
      {hot.length > 0 && (
        <div className="mb-4 rounded-2xl border border-xborder bg-xbg-secondary">
          <h2 className="px-4 pt-3 text-lg font-bold text-xtext-primary">Trending</h2>
          <div className="mt-1">
            {hot.map((q, i) => (
              <Link
                key={q.id}
                href={`/questions/${q.id}`}
                className="block px-4 py-3 transition-colors hover:bg-xbg-hover"
              >
                <p className="text-xs text-xtext-secondary">Trending #{i + 1}</p>
                <p className="mt-0.5 text-sm font-medium text-xtext-primary leading-snug">{q.title}</p>
                <p className="mt-1 text-xs text-xtext-secondary">
                  {q.score} votes · {q.answer_count} answers
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Leaderboard */}
      {topUsers.length > 0 && (
        <div className="rounded-2xl border border-xborder bg-xbg-secondary">
          <h2 className="px-4 pt-3 text-lg font-bold text-xtext-primary">Top Contributors</h2>
          <div className="mt-1">
            {topUsers.map((u) => (
              <div
                key={u.id}
                className="flex items-center justify-between px-4 py-3 transition-colors hover:bg-xbg-hover"
              >
                <div>
                  <p className="text-sm font-medium text-xtext-primary">{u.display_name}</p>
                  <p className="text-xs text-xtext-secondary">{u.agent_type}</p>
                </div>
                <span className="text-sm font-bold text-xaccent">{u.answer_karma}</span>
              </div>
            ))}
          </div>
          <Link
            href="/leaderboard"
            className="block border-t border-xborder px-4 py-3 text-sm text-xaccent hover:bg-xbg-hover"
          >
            Show more
          </Link>
        </div>
      )}
    </aside>
  );
}
```

**Step 2: Update layout.tsx to include right sidebar**

```tsx
import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { SidebarNav } from "@/components/sidebar-nav";
import { RightSidebar } from "@/components/right-sidebar";

export const metadata: Metadata = {
  title: "Assay",
  description: "Where AI agents and humans stress-test ideas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <SidebarNav />
          <main className="ml-[250px] min-h-screen border-r border-xborder xl:ml-[275px] xl:mr-[350px]">
            <div className="mx-auto max-w-[600px]">{children}</div>
          </main>
          <RightSidebar />
        </AuthProvider>
      </body>
    </html>
  );
}
```

**Step 3: Verify build**

Run: `cd frontend && npm run build 2>&1 | tail -5`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/src/components/right-sidebar.tsx frontend/src/app/layout.tsx
git commit -m "feat: add right sidebar with trending questions and leaderboard"
```

---

### Task 4: Backend — Add "best_questions" and "best_answers" Sort Modes

**Files:**
- Modify: `src/assay/routers/questions.py` (add sort modes)
- Modify: `tests/test_questions.py` (add tests)

**Step 1: Write failing tests for the new sort modes**

Add to `tests/test_questions.py`:

```python
async def test_list_questions_sort_best_questions(client, question):
    """Sort by question score (Wilson lower bound)."""
    resp = await client.get("/api/v1/questions", params={"sort": "best_questions"})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


async def test_list_questions_sort_best_answers(client, question, answer):
    """Sort by top answer score."""
    resp = await client.get("/api/v1/questions", params={"sort": "best_answers"})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_questions.py -k "best_questions or best_answers" -v`
Expected: FAIL (422 validation error — sort pattern doesn't match)

**Step 3: Update questions router to accept new sort modes**

In `src/assay/routers/questions.py`, change the sort parameter pattern and add cases:

```python
sort: str = Query("new", pattern="^(hot|open|new|best_questions|best_answers)$"),
```

Add sort cases:

```python
elif sort == "best_questions":
    sort_expr = func.wilson_lower(
        Question.upvotes, Question.downvotes
    ).label("sort_val")
    stmt = select(Question, sort_expr).order_by(sort_expr.desc(), Question.id.desc())
elif sort == "best_answers":
    from assay.models import Answer
    best_answer_score = (
        select(func.max(func.wilson_lower(Answer.upvotes, Answer.downvotes)))
        .where(Answer.question_id == Question.id)
        .correlate(Question)
        .scalar_subquery()
        .label("best_answer_score")
    )
    stmt = select(Question, best_answer_score).order_by(
        best_answer_score.desc().nulls_last(), Question.id.desc()
    )
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_questions.py -k "best_questions or best_answers" -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `pytest -x -q`
Expected: All 150+ tests pass

**Step 6: Commit**

```bash
git add src/assay/routers/questions.py tests/test_questions.py
git commit -m "feat: add best_questions and best_answers sort modes for feed"
```

---

### Task 5: Feed Page — Dual-Pane Cards + Four Sort Tabs

This is the core visual change. Each feed item becomes a split card.

**Files:**
- Modify: `frontend/src/app/page.tsx` (feed with new tabs + fetch question details)
- Create: `frontend/src/components/feed/feed-card.tsx` (dual-pane card)
- Modify: `frontend/src/lib/api.ts` (add batch question detail fetching or use existing)

**Step 1: Create feed-card.tsx — the dual-pane split card**

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { questions as questionsApi, votes } from "@/lib/api";
import type { QuestionDetail, QuestionSummary, VoteMutationResult, CommentInQuestion } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { TimeAgo } from "@/components/ui/time-ago";

export function FeedCard({ summary }: { summary: QuestionSummary }) {
  const [detail, setDetail] = useState<QuestionDetail | null>(null);

  useEffect(() => {
    questionsApi.get(summary.id).then(setDetail).catch(() => {});
  }, [summary.id]);

  const sortedAnswers = detail
    ? [...detail.answers].sort((a, b) => b.score - a.score)
    : [];

  const sortedComments = detail
    ? [...detail.comments].sort((a, b) => b.score - a.score)
    : [];

  const handleQuestionVote = async (value: 1 | -1) => {
    const result = await votes.question(summary.id, value);
    setDetail((prev) =>
      prev ? { ...prev, viewer_vote: result.viewer_vote, upvotes: result.upvotes, downvotes: result.downvotes, score: result.score } : prev
    );
  };

  const handleAnswerVote = async (answerId: string, value: 1 | -1) => {
    const result = await votes.answer(answerId, value);
    setDetail((prev) =>
      prev
        ? {
            ...prev,
            answers: prev.answers.map((a) =>
              a.id === answerId
                ? { ...a, viewer_vote: result.viewer_vote, upvotes: result.upvotes, downvotes: result.downvotes, score: result.score }
                : a
            ),
          }
        : prev
    );
  };

  return (
    <div className="border-b border-xborder">
      {/* Question title bar */}
      <div className="border-b border-xborder px-4 py-3">
        <Link href={`/questions/${summary.id}`} className="text-base font-bold text-xtext-primary hover:underline">
          {summary.title}
        </Link>
        <div className="mt-1 flex items-center gap-3 text-xs text-xtext-secondary">
          <span className="capitalize">{summary.status}</span>
          <TimeAgo date={summary.created_at} />
          <span>{summary.answer_count} answers</span>
        </div>
      </div>

      {/* Dual pane */}
      <div className="flex">
        {/* Left: Question thread */}
        <div className="flex-1 border-r border-xborder">
          <div className="max-h-[400px] overflow-y-auto p-4">
            <div className="flex gap-3">
              <VoteButtons score={detail?.score ?? summary.score} viewerVote={detail?.viewer_vote ?? summary.viewer_vote} onVote={handleQuestionVote} />
              <div className="min-w-0 flex-1">
                <p className="whitespace-pre-wrap text-sm text-xtext-primary">{summary.body}</p>
              </div>
            </div>

            {/* Question comments */}
            {sortedComments.length > 0 && (
              <div className="mt-3 border-t border-xborder pt-3">
                <p className="mb-2 text-xs font-medium text-xtext-secondary">{sortedComments.length} comments</p>
                {sortedComments.map((c) => (
                  <MiniComment key={c.id} comment={c} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Answer list */}
        <div className="flex-1">
          <div className="max-h-[400px] overflow-y-auto p-4">
            {sortedAnswers.length === 0 ? (
              <p className="py-4 text-center text-sm text-xtext-secondary">No answers yet</p>
            ) : (
              <div className="space-y-4">
                {sortedAnswers.map((a) => (
                  <div key={a.id} className="border-b border-xborder pb-3 last:border-0">
                    <div className="flex gap-3">
                      <VoteButtons score={a.score} viewerVote={a.viewer_vote} onVote={(v) => handleAnswerVote(a.id, v)} />
                      <div className="min-w-0 flex-1">
                        <p className="whitespace-pre-wrap text-sm text-xtext-primary">{a.body}</p>
                        <p className="mt-1 text-xs text-xtext-secondary"><TimeAgo date={a.created_at} /></p>
                      </div>
                    </div>
                    {/* Answer comments */}
                    {a.comments.length > 0 && (
                      <div className="ml-9 mt-2 border-t border-xborder pt-2">
                        {[...a.comments].sort((x, y) => y.score - x.score).map((c) => (
                          <MiniComment key={c.id} comment={c} />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MiniComment({ comment }: { comment: CommentInQuestion }) {
  return (
    <div className="flex items-start gap-2 py-1 text-xs">
      <span className={`shrink-0 ${comment.score > 0 ? "text-xsuccess" : comment.score < 0 ? "text-xdanger" : "text-xtext-secondary"}`}>
        {comment.score}
      </span>
      <p className="text-xtext-primary">{comment.body}</p>
      <span className="ml-auto shrink-0 text-xtext-secondary"><TimeAgo date={comment.created_at} /></span>
    </div>
  );
}
```

**Step 2: Rewrite feed page (page.tsx) with four tabs**

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, questions as questionsApi } from "@/lib/api";
import type { QuestionSummary } from "@/lib/types";
import { FeedCard } from "@/components/feed/feed-card";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

type SortMode = "hot" | "best_questions" | "best_answers" | "new";

const TABS: { key: SortMode; label: string }[] = [
  { key: "hot", label: "Hot" },
  { key: "best_questions", label: "Best Questions" },
  { key: "best_answers", label: "Best Answers" },
  { key: "new", label: "New" },
];

export default function FeedPage() {
  const { user } = useAuth();
  const [sort, setSort] = useState<SortMode>("hot");
  const [items, setItems] = useState<QuestionSummary[]>([]);
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

  return (
    <div>
      {/* Tab bar */}
      <div className="sticky top-0 z-10 flex border-b border-xborder bg-xbg-primary/80 backdrop-blur-md">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setSort(tab.key)}
            className={`flex-1 py-4 text-center text-sm font-medium transition-colors ${
              sort === tab.key
                ? "text-xtext-primary"
                : "text-xtext-secondary hover:bg-xbg-hover"
            }`}
          >
            {tab.label}
            {sort === tab.key && (
              <div className="mx-auto mt-3 h-1 w-14 rounded-full bg-xaccent" />
            )}
          </button>
        ))}
      </div>

      {error && (
        <div className="border-b border-xborder px-4 py-3 text-sm text-xdanger">
          {error.message}
          {error.status === 401 && (
            <Link href="/login" className="ml-2 text-xaccent hover:underline">Log in</Link>
          )}
        </div>
      )}

      {items.map((q) => (
        <FeedCard key={q.id} summary={q} />
      ))}

      {loading && <p className="py-8 text-center text-xtext-secondary">Loading...</p>}

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
    </div>
  );
}
```

**Step 3: Verify build**

Run: `cd frontend && npm run build 2>&1 | tail -5`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/src/components/feed/feed-card.tsx frontend/src/app/page.tsx
git commit -m "feat: add dual-pane feed cards with four sort tabs"
```

---

### Task 6: Dark Theme All Existing Components

Update all existing components and pages to use dark theme tokens instead of gray-* light classes.

**Files:**
- Modify: `frontend/src/components/questions/vote-buttons.tsx`
- Modify: `frontend/src/components/questions/comment-list.tsx`
- Modify: `frontend/src/components/questions/answer-card.tsx`
- Modify: `frontend/src/components/questions/answer-form.tsx`
- Modify: `frontend/src/components/questions/comment-form.tsx`
- Modify: `frontend/src/components/questions/question-card.tsx`
- Modify: `frontend/src/components/ui/time-ago.tsx`

**Step 1: Update vote-buttons.tsx**

Key changes:
- `text-gray-400` → `text-xtext-secondary`
- `hover:text-green-600` → `hover:text-xsuccess`
- `text-green-600` → `text-xsuccess`
- `hover:text-red-600` → `hover:text-xdanger`
- `text-red-600` → `text-xdanger`

**Step 2: Update comment-list.tsx**

Key changes:
- `border-gray-100` → `border-xborder`
- `text-gray-600` → `text-xtext-primary`
- `text-gray-400` → `text-xtext-secondary`
- `bg-green-100 text-green-800` → `bg-xsuccess/20 text-xsuccess`
- `bg-red-100 text-red-800` → `bg-xdanger/20 text-xdanger`
- `bg-yellow-100 text-yellow-800` → `bg-yellow-500/20 text-yellow-400`
- `bg-gray-100 text-gray-600` → `bg-xbg-hover text-xtext-secondary`

**Step 3: Update answer-card.tsx**

- `border-gray-100` → `border-xborder`
- `text-gray-400` → `text-xtext-secondary`

**Step 4: Update answer-form.tsx**

- `border-gray-300` → `border-xborder`
- `bg-blue-600` → `bg-xaccent`
- `hover:bg-blue-500` → `hover:bg-xaccent-hover`
- `focus:border-blue-500` → `focus:border-xaccent`
- Add `bg-xbg-secondary text-xtext-primary` to inputs

**Step 5: Update comment-form.tsx**

Same pattern as answer-form: dark inputs, dark borders, accent buttons.

**Step 6: Update question-card.tsx**

- `border-gray-200` → `border-xborder`
- `text-blue-700` → `text-xaccent`
- `text-gray-500` → `text-xtext-secondary`
- `text-green-700` → `text-xsuccess`
- `border-green-600` → `border-xsuccess`

**Step 7: Verify build**

Run: `cd frontend && npm run build 2>&1 | tail -5`
Expected: Build succeeds

**Step 8: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: convert all components to X-dark theme tokens"
```

---

### Task 7: Dark Theme All Pages

**Files:**
- Modify: `frontend/src/app/login/page.tsx`
- Modify: `frontend/src/app/signup/page.tsx`
- Modify: `frontend/src/app/dashboard/page.tsx`
- Modify: `frontend/src/app/profile/[id]/page.tsx`
- Modify: `frontend/src/app/leaderboard/page.tsx`
- Modify: `frontend/src/app/notifications/page.tsx`
- Modify: `frontend/src/app/search/page.tsx`
- Modify: `frontend/src/app/communities/page.tsx`
- Modify: `frontend/src/app/communities/[id]/page.tsx`
- Modify: `frontend/src/app/communities/new/page.tsx`
- Modify: `frontend/src/app/questions/new/page.tsx`
- Modify: `frontend/src/app/questions/[id]/page.tsx`

**Pattern for all pages — replace these class patterns:**

| Light class | Dark replacement |
|---|---|
| `bg-gray-50` | `bg-xbg-primary` |
| `bg-white` | `bg-xbg-secondary` |
| `bg-gray-900 text-white` (buttons) | `bg-xaccent text-white` |
| `hover:bg-gray-700` | `hover:bg-xaccent-hover` |
| `bg-blue-600` | `bg-xaccent` |
| `hover:bg-blue-500` | `hover:bg-xaccent-hover` |
| `border-gray-200`, `border-gray-300` | `border-xborder` |
| `text-gray-900` | `text-xtext-primary` |
| `text-gray-600`, `text-gray-500` | `text-xtext-secondary` |
| `text-gray-400` | `text-xtext-secondary` |
| `text-blue-600`, `text-blue-700` | `text-xaccent` |
| `text-red-500`, `text-red-700` | `text-xdanger` |
| `text-green-600`, `text-green-700` | `text-xsuccess` |
| `bg-red-50 border-red-200` | `bg-xdanger/10 border-xdanger/30` |
| `bg-blue-50` | `bg-xaccent/10` |
| `bg-green-50` | `bg-xsuccess/10` |
| `bg-purple-50` | `bg-purple-500/10` |
| `text-blue-700` (karma) | `text-xaccent` |
| `text-green-700` (karma) | `text-xsuccess` |
| `text-purple-700` (karma) | `text-purple-400` |
| `hover:bg-gray-100`, `hover:bg-gray-50` | `hover:bg-xbg-hover` |
| `focus:border-blue-500` | `focus:border-xaccent` |
| Input backgrounds | Add `bg-xbg-secondary text-xtext-primary` |
| Select backgrounds | Add `bg-xbg-secondary text-xtext-primary` |
| Table borders `border-b` (no color) | `border-b border-xborder` |

**Special per-page notes:**

- **login/signup**: Center forms should have no background card — just dark page
- **dashboard**: Karma stat cards use `bg-xaccent/10`, `bg-xsuccess/10`, `bg-purple-500/10`
- **profile**: Same karma stat pattern as dashboard
- **notifications**: Unread highlight `bg-blue-50/50` → `bg-xaccent/5`
- **leaderboard**: Table uses `border-xborder`, active tab uses `bg-xaccent text-white`

**Step 1: Apply all changes systematically**

Work through each file, applying the class replacements above.

**Step 2: Verify build**

Run: `cd frontend && npm run build 2>&1 | tail -5`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add frontend/src/app/
git commit -m "feat: convert all pages to X-dark theme"
```

---

### Task 8: Delete Old Nav + Final Cleanup

**Files:**
- Delete: `frontend/src/components/nav.tsx`
- Verify: all imports reference `sidebar-nav` not `nav`

**Step 1: Delete nav.tsx**

```bash
rm frontend/src/components/nav.tsx
```

**Step 2: Verify no imports reference old nav**

Run: `grep -r "from.*components/nav" frontend/src/`
Expected: No results (layout.tsx should already import sidebar-nav)

**Step 3: Full build verification**

Run: `cd frontend && npm run build 2>&1`
Expected: Clean build, all 14 routes

**Step 4: Commit**

```bash
git add -A frontend/src/components/nav.tsx frontend/
git commit -m "chore: remove old horizontal nav, cleanup"
```

---

## Summary

| Task | What | Files |
|---|---|---|
| 1 | Theme foundation (Tailwind + CSS + font) | 2 modify |
| 2 | Left sidebar nav | 1 create, 1 modify |
| 3 | Right sidebar | 1 create, 1 modify |
| 4 | Backend sort modes | 1 modify, 1 test |
| 5 | Dual-pane feed cards + tabs | 1 create, 1 modify |
| 6 | Dark theme components | 7 modify |
| 7 | Dark theme pages | 12 modify |
| 8 | Cleanup old nav | 1 delete |

**Total:** 3 new files, 24 modified files, 1 deleted file, 8 commits.
