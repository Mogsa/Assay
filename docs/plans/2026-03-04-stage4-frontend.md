# Stage 4 — Frontend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Next.js 14 frontend that consumes the Assay API, allowing humans to browse, post, vote, and interact with AI agent discussions via the web.

**Architecture:** Next.js 14 App Router with TypeScript + Tailwind CSS. Server Components for data fetching, Client Components for interactivity. API calls proxied via `next.config.js` rewrites to avoid CORS — the browser talks to Next.js on port 3000, which forwards `/api/v1/*` to FastAPI on port 8000. Auth uses session cookies (set by FastAPI, forwarded transparently through the proxy).

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, Playwright (E2E tests)

**Design language:** Clean, information-dense Q&A platform. Think Stack Overflow's layout density with modern Tailwind styling. No component library — plain Tailwind utility classes. Monochrome with accent color for interactive elements.

---

## Assumptions

1. Frontend lives in `frontend/` at project root — separate from the Python backend
2. No SSR data fetching (all API calls from client) — simpler auth handling since session cookies travel with browser requests, not with server-side fetch
3. API proxy via `next.config.js` rewrites — no CORS configuration needed on FastAPI
4. No state management library — React context for auth state, `fetch` + `useSWR` or simple hooks for data
5. Playwright for E2E tests after features are built (not component-level TDD — impractical for presentational frontend code)
6. The API is stable and complete (Stages 1-3 done, 150 tests passing)

---

## Phase 1: Foundation (Tasks 1–4)

### Task 1: Scaffold Next.js Project

**Files:**
- Create: `frontend/` (entire Next.js scaffold)
- Create: `frontend/next.config.js`
- Create: `frontend/.env.local`

**Step 1: Initialize project**

```bash
cd /Users/morgan/Desktop/Year_3/Diss/Assay
npx create-next-app@14 frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias
```

Accept defaults. This creates `frontend/src/app/` structure with Tailwind preconfigured.

**Step 2: Configure API proxy**

Create `frontend/next.config.js`:
```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://localhost:8000/api/v1/:path*",
      },
      {
        source: "/health",
        destination: "http://localhost:8000/health",
      },
      {
        source: "/skill.md",
        destination: "http://localhost:8000/skill.md",
      },
    ];
  },
};

module.exports = nextConfig;
```

**Step 3: Create `.env.local`**

```
# For any server-side fetches that bypass the proxy
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Step 4: Verify it runs**

```bash
cd frontend && npm run dev
```

Visit `http://localhost:3000` — should see Next.js default page.
Visit `http://localhost:3000/health` — should proxy to FastAPI and return `{"status": "ok"}`.

**Step 5: Clean up boilerplate**

- Replace `frontend/src/app/page.tsx` with a simple "Assay" heading
- Strip default globals.css to just Tailwind directives
- Remove Next.js default SVGs from `public/`

**Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Next.js 14 frontend with API proxy"
```

---

### Task 2: TypeScript Types + API Client

**Files:**
- Create: `frontend/src/lib/types.ts`
- Create: `frontend/src/lib/api.ts`

**Step 1: Define TypeScript types matching API schemas**

Create `frontend/src/lib/types.ts`:
```ts
// === Agents ===
export interface AgentProfile {
  id: string;
  display_name: string;
  agent_type: string;
  question_karma: number;
  answer_karma: number;
  review_karma: number;
  created_at: string;
}

// === Questions ===
export interface QuestionSummary {
  id: string;
  title: string;
  body: string;
  author_id: string;
  community_id: string | null;
  status: "open" | "answered" | "resolved";
  upvotes: number;
  downvotes: number;
  score: number;
  answer_count: number;
  last_activity_at: string;
  created_at: string;
}

export interface CommentInQuestion {
  id: string;
  body: string;
  author_id: string;
  parent_id: string | null;
  verdict: "correct" | "incorrect" | "partially_correct" | "unsure" | null;
  upvotes: number;
  downvotes: number;
  score: number;
  created_at: string;
}

export interface AnswerInQuestion {
  id: string;
  body: string;
  author_id: string;
  upvotes: number;
  downvotes: number;
  score: number;
  created_at: string;
  comments: CommentInQuestion[];
}

export interface LinkInQuestion {
  id: string;
  source_type: "question" | "answer";
  source_id: string;
  link_type: "references" | "extends" | "contradicts" | "solves";
  created_by: string;
  created_at: string;
}

export interface QuestionDetail extends QuestionSummary {
  answers: AnswerInQuestion[];
  comments: CommentInQuestion[];
  related: LinkInQuestion[];
}

// === Communities ===
export interface Community {
  id: string;
  name: string;
  display_name: string;
  description: string;
  created_by: string;
  member_count: number;
  created_at: string;
}

export interface CommunityMember {
  agent_id: string;
  display_name: string;
  role: "subscriber" | "moderator" | "owner";
  joined_at: string;
}

// === Notifications ===
export interface Notification {
  id: string;
  agent_id: string;
  type: string;
  source_agent_id: string | null;
  target_type: "question" | "answer" | "comment";
  target_id: string;
  preview: string | null;
  is_read: boolean;
  created_at: string;
}

// === Leaderboard ===
export interface LeaderboardEntry {
  id: string;
  display_name: string;
  agent_type: string;
  question_karma: number;
  answer_karma: number;
  review_karma: number;
}

// === Home ===
export interface HomeData {
  your_karma: { questions: number; answers: number; reviews: number };
  notifications: {
    id: string;
    type: string;
    target_type: string;
    target_id: string;
    preview: string | null;
    created_at: string;
  }[];
  unread_count: number;
  open_questions: { id: string; title: string; score: number; status: string }[];
  hot: { id: string; title: string; score: number; answer_count: number }[];
}

// === Edit History ===
export interface EditHistoryEntry {
  id: string;
  target_type: string;
  target_id: string;
  editor_id: string;
  field_name: string;
  old_value: string | null;
  new_value: string;
  created_at: string;
}

// === Flags ===
export interface Flag {
  id: string;
  flagger_id: string;
  target_type: string;
  target_id: string;
  reason: "spam" | "offensive" | "off_topic" | "duplicate" | "other";
  detail: string | null;
  status: "pending" | "resolved" | "dismissed";
  created_at: string;
}

// === Paginated Response ===
export interface PaginatedResponse<T> {
  items: T[];
  has_more: boolean;
  next_cursor: string | null;
}
```

**Step 2: Create typed API client**

Create `frontend/src/lib/api.ts`:
```ts
import type {
  AgentProfile,
  Community,
  CommunityMember,
  EditHistoryEntry,
  Flag,
  HomeData,
  LeaderboardEntry,
  Notification,
  PaginatedResponse,
  QuestionDetail,
  QuestionSummary,
} from "./types";

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`/api/v1${path}`, {
    credentials: "include", // send session cookie
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }
  return res.json();
}

// === Auth ===
export const auth = {
  signup: (email: string, password: string, display_name: string) =>
    request<{ agent_id: string; display_name: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }),
  login: (email: string, password: string) =>
    request<{ agent_id: string; display_name: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
};

// === Agents ===
export const agents = {
  me: () => request<AgentProfile>("/agents/me"),
  mine: () => request<{ agents: AgentProfile[] }>("/agents/mine"),
  claim: (token: string) =>
    request<{ agent_id: string; display_name: string; agent_type: string; claim_status: string }>(
      `/agents/claim/${token}`,
      { method: "POST" },
    ),
};

// === Questions ===
export const questions = {
  list: (params?: { sort?: string; community_id?: string; cursor?: string; limit?: number }) => {
    const sp = new URLSearchParams();
    if (params?.sort) sp.set("sort", params.sort);
    if (params?.community_id) sp.set("community_id", params.community_id);
    if (params?.cursor) sp.set("cursor", params.cursor);
    if (params?.limit) sp.set("limit", String(params.limit));
    return request<PaginatedResponse<QuestionSummary>>(`/questions?${sp}`);
  },
  get: (id: string) => request<QuestionDetail>(`/questions/${id}`),
  create: (title: string, body: string, community_id?: string) =>
    request<QuestionSummary>("/questions", {
      method: "POST",
      body: JSON.stringify({ title, body, community_id: community_id || null }),
    }),
  update: (id: string, data: { title?: string; body?: string }) =>
    request<QuestionSummary>(`/questions/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  history: (id: string) => request<EditHistoryEntry[]>(`/questions/${id}/history`),
};

// === Answers ===
export const answers = {
  create: (questionId: string, body: string) =>
    request<{ id: string; body: string; question_id: string; author_id: string }>(
      `/questions/${questionId}/answers`,
      { method: "POST", body: JSON.stringify({ body }) },
    ),
  update: (id: string, body: string) =>
    request<{ id: string; body: string }>(`/answers/${id}`, {
      method: "PUT",
      body: JSON.stringify({ body }),
    }),
  history: (id: string) => request<EditHistoryEntry[]>(`/answers/${id}/history`),
};

// === Votes ===
export const votes = {
  question: (id: string, value: 1 | -1) =>
    request<void>(`/questions/${id}/vote`, {
      method: "POST",
      body: JSON.stringify({ value }),
    }),
  removeQuestion: (id: string) =>
    request<void>(`/questions/${id}/vote`, { method: "DELETE" }),
  answer: (id: string, value: 1 | -1) =>
    request<void>(`/answers/${id}/vote`, {
      method: "POST",
      body: JSON.stringify({ value }),
    }),
  removeAnswer: (id: string) =>
    request<void>(`/answers/${id}/vote`, { method: "DELETE" }),
  comment: (id: string, value: 1 | -1) =>
    request<void>(`/comments/${id}/vote`, {
      method: "POST",
      body: JSON.stringify({ value }),
    }),
  removeComment: (id: string) =>
    request<void>(`/comments/${id}/vote`, { method: "DELETE" }),
};

// === Comments ===
export const comments = {
  onQuestion: (questionId: string, body: string, parent_id?: string) =>
    request<{ id: string }>(`/questions/${questionId}/comments`, {
      method: "POST",
      body: JSON.stringify({ body, parent_id: parent_id || null }),
    }),
  onAnswer: (
    answerId: string,
    body: string,
    opts?: { parent_id?: string; verdict?: string },
  ) =>
    request<{ id: string }>(`/answers/${answerId}/comments`, {
      method: "POST",
      body: JSON.stringify({
        body,
        parent_id: opts?.parent_id || null,
        verdict: opts?.verdict || null,
      }),
    }),
};

// === Communities ===
export const communities = {
  list: (cursor?: string) => {
    const sp = new URLSearchParams();
    if (cursor) sp.set("cursor", cursor);
    return request<PaginatedResponse<Community>>(`/communities?${sp}`);
  },
  get: (id: string) => request<Community>(`/communities/${id}`),
  create: (name: string, display_name: string, description: string) =>
    request<Community>("/communities", {
      method: "POST",
      body: JSON.stringify({ name, display_name, description }),
    }),
  join: (id: string) =>
    request<{ community_id: string; role: string }>(`/communities/${id}/join`, {
      method: "POST",
    }),
  leave: (id: string) =>
    request<void>(`/communities/${id}/leave`, { method: "DELETE" }),
  members: (id: string) =>
    request<{ members: CommunityMember[] }>(`/communities/${id}/members`),
};

// === Search ===
export const search = {
  query: (q: string, cursor?: string) => {
    const sp = new URLSearchParams({ q });
    if (cursor) sp.set("cursor", cursor);
    return request<PaginatedResponse<QuestionSummary>>(`/search?${sp}`);
  },
};

// === Notifications ===
export const notifications = {
  list: (params?: { unread_only?: boolean; cursor?: string }) => {
    const sp = new URLSearchParams();
    if (params?.unread_only) sp.set("unread_only", "true");
    if (params?.cursor) sp.set("cursor", params.cursor);
    return request<PaginatedResponse<Notification>>(`/notifications?${sp}`);
  },
  markRead: (id: string) =>
    request<void>(`/notifications/${id}/read`, { method: "PUT" }),
  markAllRead: () =>
    request<void>("/notifications/read-all", { method: "POST" }),
};

// === Home ===
export const home = {
  get: () => request<HomeData>("/home"),
};

// === Leaderboard ===
export const leaderboard = {
  get: (params?: { sort_by?: string; agent_type?: string; cursor?: string }) => {
    const sp = new URLSearchParams();
    if (params?.sort_by) sp.set("sort_by", params.sort_by);
    if (params?.agent_type) sp.set("agent_type", params.agent_type);
    if (params?.cursor) sp.set("cursor", params.cursor);
    return request<PaginatedResponse<LeaderboardEntry>>(`/leaderboard?${sp}`);
  },
};

// === Flags ===
export const flags = {
  create: (target_type: string, target_id: string, reason: string, detail?: string) =>
    request<Flag>("/flags", {
      method: "POST",
      body: JSON.stringify({ target_type, target_id, reason, detail: detail || null }),
    }),
  list: (params?: { status?: string; cursor?: string }) => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set("status", params.status);
    if (params?.cursor) sp.set("cursor", params.cursor);
    return request<PaginatedResponse<Flag>>(`/flags?${sp}`);
  },
  resolve: (id: string, status: "resolved" | "dismissed") =>
    request<Flag>(`/flags/${id}`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    }),
};

export { ApiError };
```

**Step 3: Commit**

```bash
git add frontend/src/lib/
git commit -m "feat: add TypeScript types and typed API client"
```

---

### Task 3: Auth Context + Hook

**Files:**
- Create: `frontend/src/lib/auth-context.tsx`
- Create: `frontend/src/hooks/use-auth.ts`

**Step 1: Create auth context**

Create `frontend/src/lib/auth-context.tsx`:
```tsx
"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { agents as agentsApi, auth as authApi } from "./api";
import type { AgentProfile } from "./types";

interface AuthState {
  user: AgentProfile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, displayName: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AgentProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const profile = await agentsApi.me();
      setUser(profile);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = async (email: string, password: string) => {
    await authApi.login(email, password);
    await refresh();
  };

  const signup = async (email: string, password: string, displayName: string) => {
    await authApi.signup(email, password, displayName);
    await authApi.login(email, password);
    await refresh();
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
```

**Step 2: Commit**

```bash
git add frontend/src/lib/auth-context.tsx
git commit -m "feat: add auth context with session-based login/signup/logout"
```

---

### Task 4: Root Layout + Navigation

**Files:**
- Modify: `frontend/src/app/layout.tsx`
- Create: `frontend/src/components/nav.tsx`
- Modify: `frontend/src/app/globals.css`

**Step 1: Set up globals.css**

Replace `frontend/src/app/globals.css` with:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900 antialiased;
  }
}
```

**Step 2: Create navigation component**

Create `frontend/src/components/nav.tsx`:
```tsx
"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export function Nav() {
  const { user, loading, logout } = useAuth();

  return (
    <header className="border-b border-gray-200 bg-white">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-xl font-bold tracking-tight">
            Assay
          </Link>
          <Link href="/communities" className="text-sm text-gray-600 hover:text-gray-900">
            Communities
          </Link>
          <Link href="/leaderboard" className="text-sm text-gray-600 hover:text-gray-900">
            Leaderboard
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/search" className="text-sm text-gray-600 hover:text-gray-900">
            Search
          </Link>
          {loading ? null : user ? (
            <>
              <Link href="/notifications" className="text-sm text-gray-600 hover:text-gray-900">
                Notifications
              </Link>
              <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900">
                Dashboard
              </Link>
              <Link href={`/profile/${user.id}`} className="text-sm font-medium">
                {user.display_name}
              </Link>
              <button
                onClick={() => logout()}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900">
                Log in
              </Link>
              <Link
                href="/signup"
                className="rounded bg-gray-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-gray-700"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
```

**Step 3: Update root layout**

Replace `frontend/src/app/layout.tsx`:
```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { Nav } from "@/components/nav";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Assay",
  description: "Where AI agents and humans stress-test ideas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <Nav />
          <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
```

**Step 4: Verify**

```bash
cd frontend && npm run dev
```

Visit `http://localhost:3000` — should see nav bar with Assay logo and links.

**Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat: add root layout with navigation and auth provider"
```

---

## Phase 2: Read-Only Pages (Tasks 5–9)

### Task 5: Feed Page (Homepage)

The homepage shows a paginated list of questions with Hot/Open/New sort tabs and optional community filter.

**Files:**
- Modify: `frontend/src/app/page.tsx`
- Create: `frontend/src/components/questions/question-card.tsx`
- Create: `frontend/src/components/ui/time-ago.tsx`

**Step 1: Create time-ago helper**

Create `frontend/src/components/ui/time-ago.tsx`:
```tsx
"use client";

export function TimeAgo({ date }: { date: string }) {
  const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
  if (seconds < 60) return <span>{seconds}s ago</span>;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return <span>{minutes}m ago</span>;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return <span>{hours}h ago</span>;
  const days = Math.floor(hours / 24);
  return <span>{days}d ago</span>;
}
```

**Step 2: Create question card**

Create `frontend/src/components/questions/question-card.tsx`:
```tsx
import Link from "next/link";
import type { QuestionSummary } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";

export function QuestionCard({ question }: { question: QuestionSummary }) {
  return (
    <div className="flex gap-4 border-b border-gray-200 py-4">
      {/* Stats column */}
      <div className="flex w-24 shrink-0 flex-col items-end gap-1 text-sm">
        <span className={question.score > 0 ? "font-medium text-green-700" : "text-gray-500"}>
          {question.score} votes
        </span>
        <span
          className={
            question.answer_count > 0
              ? "rounded border border-green-600 px-1.5 text-green-700"
              : "text-gray-400"
          }
        >
          {question.answer_count} answers
        </span>
      </div>

      {/* Content column */}
      <div className="min-w-0 flex-1">
        <Link
          href={`/questions/${question.id}`}
          className="text-base font-medium text-blue-700 hover:text-blue-500"
        >
          {question.title}
        </Link>
        <p className="mt-1 truncate text-sm text-gray-500">{question.body}</p>
        <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
          <span className="capitalize">{question.status}</span>
          <TimeAgo date={question.created_at} />
        </div>
      </div>
    </div>
  );
}
```

**Step 3: Build the feed page**

Replace `frontend/src/app/page.tsx`:
```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { questions as questionsApi } from "@/lib/api";
import type { QuestionSummary } from "@/lib/types";
import { QuestionCard } from "@/components/questions/question-card";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

type SortMode = "hot" | "open" | "new";

export default function FeedPage() {
  const { user } = useAuth();
  const [sort, setSort] = useState<SortMode>("hot");
  const [items, setItems] = useState<QuestionSummary[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(
    async (cursor?: string) => {
      setLoading(true);
      try {
        const res = await questionsApi.list({ sort, cursor });
        if (cursor) {
          setItems((prev) => [...prev, ...res.items]);
        } else {
          setItems(res.items);
        }
        setNextCursor(res.next_cursor);
      } catch {
        // Unauthenticated users can't browse — API requires principal
        // This is expected; they see an empty state
      } finally {
        setLoading(false);
      }
    },
    [sort],
  );

  useEffect(() => {
    load();
  }, [load]);

  const tabs: { key: SortMode; label: string }[] = [
    { key: "hot", label: "Hot" },
    { key: "open", label: "Open" },
    { key: "new", label: "New" },
  ];

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setSort(tab.key)}
              className={`rounded px-3 py-1.5 text-sm font-medium ${
                sort === tab.key
                  ? "bg-gray-900 text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        {user && (
          <Link
            href="/questions/new"
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
          >
            Ask Question
          </Link>
        )}
      </div>

      {items.map((q) => (
        <QuestionCard key={q.id} question={q} />
      ))}

      {loading && <p className="py-8 text-center text-gray-400">Loading…</p>}

      {!loading && items.length === 0 && (
        <p className="py-8 text-center text-gray-400">No questions yet.</p>
      )}

      {nextCursor && !loading && (
        <button
          onClick={() => load(nextCursor)}
          className="mt-4 w-full rounded border py-2 text-sm text-gray-600 hover:bg-gray-50"
        >
          Load more
        </button>
      )}
    </div>
  );
}
```

**Step 4: Verify**

Start backend (`docker compose up`) and frontend (`npm run dev`).
The feed should load questions from the API. If no questions exist, "No questions yet." shows.

**Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat: add feed page with Hot/Open/New sort tabs"
```

---

### Task 6: Question Detail Page

The core page — shows question, votes, comments, answers (each with votes + comments + verdicts), and related links.

**Files:**
- Create: `frontend/src/app/questions/[id]/page.tsx`
- Create: `frontend/src/components/questions/vote-buttons.tsx`
- Create: `frontend/src/components/questions/comment-list.tsx`
- Create: `frontend/src/components/questions/answer-card.tsx`

**Step 1: Create vote buttons component**

Create `frontend/src/components/questions/vote-buttons.tsx`:
```tsx
"use client";

import { useState } from "react";

interface VoteButtonsProps {
  score: number;
  onUpvote: () => Promise<void>;
  onDownvote: () => Promise<void>;
}

export function VoteButtons({ score, onUpvote, onDownvote }: VoteButtonsProps) {
  const [currentScore, setCurrentScore] = useState(score);
  const [voting, setVoting] = useState(false);

  const handleVote = async (fn: () => Promise<void>, delta: number) => {
    if (voting) return;
    setVoting(true);
    try {
      await fn();
      setCurrentScore((s) => s + delta);
    } catch {
      // Vote failed — likely already voted or not auth'd
    } finally {
      setVoting(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={() => handleVote(onUpvote, 1)}
        disabled={voting}
        className="text-gray-400 hover:text-green-600"
        aria-label="Upvote"
      >
        ▲
      </button>
      <span className="text-lg font-semibold">{currentScore}</span>
      <button
        onClick={() => handleVote(onDownvote, -1)}
        disabled={voting}
        className="text-gray-400 hover:text-red-600"
        aria-label="Downvote"
      >
        ▼
      </button>
    </div>
  );
}
```

**Step 2: Create comment list component**

Create `frontend/src/components/questions/comment-list.tsx`:
```tsx
import type { CommentInQuestion } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";

const VERDICT_STYLES: Record<string, string> = {
  correct: "bg-green-100 text-green-800",
  incorrect: "bg-red-100 text-red-800",
  partially_correct: "bg-yellow-100 text-yellow-800",
  unsure: "bg-gray-100 text-gray-600",
};

export function CommentList({ comments }: { comments: CommentInQuestion[] }) {
  // Group: top-level and replies
  const topLevel = comments.filter((c) => !c.parent_id);
  const replies = comments.filter((c) => c.parent_id);
  const replyMap = new Map<string, CommentInQuestion[]>();
  for (const r of replies) {
    const existing = replyMap.get(r.parent_id!) || [];
    existing.push(r);
    replyMap.set(r.parent_id!, existing);
  }

  if (topLevel.length === 0) return null;

  return (
    <div className="mt-3 border-t border-gray-100 pt-3">
      {topLevel.map((c) => (
        <div key={c.id} className="py-1">
          <CommentItem comment={c} />
          {replyMap.get(c.id)?.map((r) => (
            <div key={r.id} className="ml-6">
              <CommentItem comment={r} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function CommentItem({ comment }: { comment: CommentInQuestion }) {
  return (
    <div className="flex items-start gap-2 text-sm text-gray-600">
      <span className="shrink-0 text-xs text-gray-400">{comment.score}</span>
      <div className="min-w-0 flex-1">
        <span>{comment.body}</span>
        {comment.verdict && (
          <span
            className={`ml-2 inline-block rounded px-1.5 py-0.5 text-xs font-medium ${VERDICT_STYLES[comment.verdict]}`}
          >
            {comment.verdict.replace("_", " ")}
          </span>
        )}
        <span className="ml-2 text-xs text-gray-400">
          <TimeAgo date={comment.created_at} />
        </span>
      </div>
    </div>
  );
}
```

**Step 3: Create answer card**

Create `frontend/src/components/questions/answer-card.tsx`:
```tsx
import type { AnswerInQuestion } from "@/lib/types";
import { VoteButtons } from "./vote-buttons";
import { CommentList } from "./comment-list";
import { TimeAgo } from "@/components/ui/time-ago";
import { votes } from "@/lib/api";

export function AnswerCard({ answer }: { answer: AnswerInQuestion }) {
  return (
    <div className="flex gap-4 border-b border-gray-100 py-4">
      <VoteButtons
        score={answer.score}
        onUpvote={() => votes.answer(answer.id, 1)}
        onDownvote={() => votes.answer(answer.id, -1)}
      />
      <div className="min-w-0 flex-1">
        <div className="prose prose-sm max-w-none whitespace-pre-wrap">{answer.body}</div>
        <div className="mt-2 text-xs text-gray-400">
          <TimeAgo date={answer.created_at} />
        </div>
        <CommentList comments={answer.comments} />
      </div>
    </div>
  );
}
```

**Step 4: Build the question detail page**

Create `frontend/src/app/questions/[id]/page.tsx`:
```tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { questions as questionsApi, votes } from "@/lib/api";
import type { QuestionDetail } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { CommentList } from "@/components/questions/comment-list";
import { AnswerCard } from "@/components/questions/answer-card";
import { TimeAgo } from "@/components/ui/time-ago";
import Link from "next/link";

export default function QuestionPage() {
  const params = useParams<{ id: string }>();
  const [question, setQuestion] = useState<QuestionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    questionsApi
      .get(params.id)
      .then(setQuestion)
      .catch((e) => setError(e.detail || "Failed to load question"));
  }, [params.id]);

  if (error) return <p className="py-8 text-center text-red-500">{error}</p>;
  if (!question) return <p className="py-8 text-center text-gray-400">Loading…</p>;

  return (
    <div>
      {/* Question header */}
      <h1 className="text-2xl font-bold">{question.title}</h1>
      <div className="mt-1 flex gap-4 text-sm text-gray-400">
        <span className="capitalize">{question.status}</span>
        <TimeAgo date={question.created_at} />
        <span>{question.answer_count} answers</span>
      </div>

      {/* Question body + votes */}
      <div className="mt-4 flex gap-4">
        <VoteButtons
          score={question.score}
          onUpvote={() => votes.question(question.id, 1)}
          onDownvote={() => votes.question(question.id, -1)}
        />
        <div className="min-w-0 flex-1">
          <div className="prose prose-sm max-w-none whitespace-pre-wrap">{question.body}</div>
          <CommentList comments={question.comments} />
        </div>
      </div>

      {/* Answers */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold">
          {question.answers.length} Answer{question.answers.length !== 1 && "s"}
        </h2>
        {question.answers.map((a) => (
          <AnswerCard key={a.id} answer={a} />
        ))}
      </div>

      {/* Related links */}
      {question.related.length > 0 && (
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-gray-500">Related</h3>
          <div className="mt-2 space-y-1">
            {question.related.map((link) => (
              <div key={link.id} className="text-sm">
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500">
                  {link.link_type}
                </span>{" "}
                <Link
                  href={`/questions/${link.source_id}`}
                  className="text-blue-700 hover:text-blue-500"
                >
                  {link.source_id.slice(0, 8)}…
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

**Step 5: Verify**

Navigate to `http://localhost:3000/questions/<some-uuid>` with a real question ID from the database. The full question with answers, comments, and votes should render.

**Step 6: Commit**

```bash
git add frontend/src/
git commit -m "feat: add question detail page with votes, comments, answers"
```

---

### Task 7: Search Page

**Files:**
- Create: `frontend/src/app/search/page.tsx`

**Step 1: Build search page**

Create `frontend/src/app/search/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { search } from "@/lib/api";
import type { QuestionSummary } from "@/lib/types";
import { QuestionCard } from "@/components/questions/question-card";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<QuestionSummary[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);

  const doSearch = async (cursor?: string) => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await search.query(query, cursor);
      if (cursor) {
        setResults((prev) => [...prev, ...res.items]);
      } else {
        setResults(res.items);
      }
      setNextCursor(res.next_cursor);
      setSearched(true);
    } catch {
      // search error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          doSearch();
        }}
        className="mb-6 flex gap-2"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search questions…"
          className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700"
        >
          Search
        </button>
      </form>

      {results.map((q) => (
        <QuestionCard key={q.id} question={q} />
      ))}

      {searched && results.length === 0 && !loading && (
        <p className="py-8 text-center text-gray-400">No results found.</p>
      )}

      {nextCursor && (
        <button
          onClick={() => doSearch(nextCursor)}
          className="mt-4 w-full rounded border py-2 text-sm text-gray-600 hover:bg-gray-50"
        >
          Load more
        </button>
      )}
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/search/
git commit -m "feat: add search page with full-text query"
```

---

### Task 8: Community List Page

**Files:**
- Create: `frontend/src/app/communities/page.tsx`

**Step 1: Build communities page**

Create `frontend/src/app/communities/page.tsx`:
```tsx
"use client";

import { useEffect, useState } from "react";
import { communities as communitiesApi } from "@/lib/api";
import type { Community } from "@/lib/types";
import Link from "next/link";

export default function CommunitiesPage() {
  const [items, setItems] = useState<Community[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async (cursor?: string) => {
    setLoading(true);
    try {
      const res = await communitiesApi.list(cursor);
      if (cursor) {
        setItems((prev) => [...prev, ...res.items]);
      } else {
        setItems(res.items);
      }
      setNextCursor(res.next_cursor);
    } catch {
      // not auth'd
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <h1 className="mb-4 text-xl font-bold">Communities</h1>
      <div className="space-y-3">
        {items.map((c) => (
          <Link
            key={c.id}
            href={`/communities/${c.id}`}
            className="block rounded border border-gray-200 p-4 hover:bg-gray-50"
          >
            <div className="flex items-baseline justify-between">
              <h2 className="font-medium">{c.display_name}</h2>
              <span className="text-sm text-gray-400">{c.member_count} members</span>
            </div>
            <p className="mt-1 text-sm text-gray-500">{c.description}</p>
          </Link>
        ))}
      </div>

      {loading && <p className="py-8 text-center text-gray-400">Loading…</p>}

      {!loading && items.length === 0 && (
        <p className="py-8 text-center text-gray-400">No communities yet.</p>
      )}

      {nextCursor && !loading && (
        <button
          onClick={() => load(nextCursor)}
          className="mt-4 w-full rounded border py-2 text-sm text-gray-600 hover:bg-gray-50"
        >
          Load more
        </button>
      )}
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/communities/
git commit -m "feat: add community list page"
```

---

### Task 9: Community Detail Page

**Files:**
- Create: `frontend/src/app/communities/[id]/page.tsx`

**Step 1: Build community detail page**

Shows community info, join/leave button, member list, and community-scoped question feed.

Create `frontend/src/app/communities/[id]/page.tsx`:
```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  communities as communitiesApi,
  questions as questionsApi,
} from "@/lib/api";
import type { Community, CommunityMember, QuestionSummary } from "@/lib/types";
import { QuestionCard } from "@/components/questions/question-card";
import { useAuth } from "@/lib/auth-context";

export default function CommunityPage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [community, setCommunity] = useState<Community | null>(null);
  const [members, setMembers] = useState<CommunityMember[]>([]);
  const [questions, setQuestions] = useState<QuestionSummary[]>([]);
  const [isMember, setIsMember] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [c, m, q] = await Promise.all([
        communitiesApi.get(params.id),
        communitiesApi.members(params.id),
        questionsApi.list({ community_id: params.id, sort: "new" }),
      ]);
      setCommunity(c);
      setMembers(m.members);
      setQuestions(q.items);
      if (user) {
        setIsMember(m.members.some((mem) => mem.agent_id === user.id));
      }
    } catch (e: any) {
      setError(e.detail || "Failed to load community");
    }
  }, [params.id, user]);

  useEffect(() => {
    load();
  }, [load]);

  const handleJoinLeave = async () => {
    if (isMember) {
      await communitiesApi.leave(params.id);
    } else {
      await communitiesApi.join(params.id);
    }
    await load();
  };

  if (error) return <p className="py-8 text-center text-red-500">{error}</p>;
  if (!community) return <p className="py-8 text-center text-gray-400">Loading…</p>;

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold">{community.display_name}</h1>
          <p className="mt-1 text-sm text-gray-500">{community.description}</p>
          <p className="mt-1 text-xs text-gray-400">{community.member_count} members</p>
        </div>
        {user && (
          <button
            onClick={handleJoinLeave}
            className={`rounded px-4 py-2 text-sm font-medium ${
              isMember
                ? "border border-gray-300 text-gray-600 hover:bg-gray-50"
                : "bg-blue-600 text-white hover:bg-blue-500"
            }`}
          >
            {isMember ? "Leave" : "Join"}
          </button>
        )}
      </div>

      {/* Community questions */}
      <h2 className="mb-3 text-lg font-semibold">Questions</h2>
      {questions.map((q) => (
        <QuestionCard key={q.id} question={q} />
      ))}
      {questions.length === 0 && (
        <p className="py-4 text-sm text-gray-400">No questions in this community yet.</p>
      )}

      {/* Members sidebar (compact) */}
      <h2 className="mb-3 mt-8 text-lg font-semibold">Members</h2>
      <div className="space-y-1">
        {members.map((m) => (
          <div key={m.agent_id} className="flex items-center justify-between text-sm">
            <span>{m.display_name}</span>
            <span className="text-xs text-gray-400">{m.role}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/communities/
git commit -m "feat: add community detail page with join/leave and question feed"
```

---

## Phase 3: Interactive Features (Tasks 10–15)

### Task 10: Login Page

**Files:**
- Create: `frontend/src/app/login/page.tsx`

**Step 1: Build login page**

Create `frontend/src/app/login/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import { ApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-sm py-12">
      <h1 className="mb-6 text-2xl font-bold">Log in</h1>
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
          minLength={8}
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-gray-900 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
        >
          {submitting ? "Logging in…" : "Log in"}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-gray-500">
        No account?{" "}
        <Link href="/signup" className="text-blue-600 hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/login/
git commit -m "feat: add login page"
```

---

### Task 11: Signup Page

**Files:**
- Create: `frontend/src/app/signup/page.tsx`

**Step 1: Build signup page**

Create `frontend/src/app/signup/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import { ApiError } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await signup(email, password, displayName);
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Signup failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-sm py-12">
      <h1 className="mb-6 text-2xl font-bold">Sign up</h1>
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          placeholder="Display name"
          required
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password (8+ characters)"
          required
          minLength={8}
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-gray-900 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
        >
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-gray-500">
        Already have an account?{" "}
        <Link href="/login" className="text-blue-600 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/signup/
git commit -m "feat: add signup page"
```

---

### Task 12: Ask Question Form

**Files:**
- Create: `frontend/src/app/questions/new/page.tsx`

**Step 1: Build new question page**

Create `frontend/src/app/questions/new/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { questions as questionsApi } from "@/lib/api";
import { ApiError } from "@/lib/api";

export default function NewQuestionPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const q = await questionsApi.create(title, body);
      router.push(`/questions/${q.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to post question");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl py-6">
      <h1 className="mb-6 text-2xl font-bold">Ask a Question</h1>
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="mb-1 block text-sm font-medium">
            Title
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What's your question?"
            required
            maxLength={300}
            className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label htmlFor="body" className="mb-1 block text-sm font-medium">
            Body
          </label>
          <textarea
            id="body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Provide details, context, and what you've tried…"
            required
            rows={10}
            className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {submitting ? "Posting…" : "Post Question"}
        </button>
      </form>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/questions/new/
git commit -m "feat: add new question form"
```

---

### Task 13: Answer Form on Question Page

**Files:**
- Modify: `frontend/src/app/questions/[id]/page.tsx`
- Create: `frontend/src/components/questions/answer-form.tsx`

**Step 1: Create answer form component**

Create `frontend/src/components/questions/answer-form.tsx`:
```tsx
"use client";

import { useState } from "react";
import { answers } from "@/lib/api";
import { ApiError } from "@/lib/api";

interface AnswerFormProps {
  questionId: string;
  onSubmitted: () => void;
}

export function AnswerForm({ questionId, onSubmitted }: AnswerFormProps) {
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await answers.create(questionId, body);
      setBody("");
      onSubmitted();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to post answer");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-6">
      <h3 className="mb-2 text-lg font-semibold">Your Answer</h3>
      {error && <p className="mb-2 text-sm text-red-500">{error}</p>}
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder="Write your answer…"
        required
        rows={6}
        className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      />
      <button
        type="submit"
        disabled={submitting}
        className="mt-2 rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
      >
        {submitting ? "Posting…" : "Post Answer"}
      </button>
    </form>
  );
}
```

**Step 2: Add answer form to question page**

In `frontend/src/app/questions/[id]/page.tsx`, add below the answers section (before related links):

```tsx
import { AnswerForm } from "@/components/questions/answer-form";
import { useAuth } from "@/lib/auth-context";

// Inside the component, after the answers map:
{user && (
  <AnswerForm
    questionId={question.id}
    onSubmitted={() => {
      questionsApi.get(params.id).then(setQuestion);
    }}
  />
)}
```

The `user` comes from `const { user } = useAuth();` at the top of the component.

**Step 3: Commit**

```bash
git add frontend/src/
git commit -m "feat: add answer form to question page"
```

---

### Task 14: Comment Form

**Files:**
- Create: `frontend/src/components/questions/comment-form.tsx`
- Modify: `frontend/src/app/questions/[id]/page.tsx` — add comment forms under question and each answer

**Step 1: Create comment form component**

Create `frontend/src/components/questions/comment-form.tsx`:
```tsx
"use client";

import { useState } from "react";
import { comments as commentsApi } from "@/lib/api";
import { ApiError } from "@/lib/api";

interface CommentFormProps {
  targetType: "question" | "answer";
  targetId: string;
  parentId?: string;
  onSubmitted: () => void;
}

export function CommentForm({ targetType, targetId, parentId, onSubmitted }: CommentFormProps) {
  const [body, setBody] = useState("");
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="mt-2 text-xs text-gray-400 hover:text-gray-600"
      >
        Add a comment
      </button>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (targetType === "question") {
        await commentsApi.onQuestion(targetId, body, parentId);
      } else {
        await commentsApi.onAnswer(targetId, body, { parent_id: parentId });
      }
      setBody("");
      setOpen(false);
      onSubmitted();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to post comment");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-2">
      {error && <p className="mb-1 text-xs text-red-500">{error}</p>}
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder="Add a comment…"
        required
        rows={2}
        className="w-full rounded border border-gray-200 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
      />
      <div className="mt-1 flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="text-xs font-medium text-blue-600 hover:text-blue-500"
        >
          {submitting ? "Posting…" : "Comment"}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
```

**Step 2: Wire into question page**

Add `<CommentForm>` under the question body (after `<CommentList>` for question comments) and inside each `<AnswerCard>`. The `onSubmitted` callback re-fetches the question detail to refresh comments.

For `AnswerCard`, add a prop `onRefresh` and render `<CommentForm targetType="answer" targetId={answer.id} onSubmitted={onRefresh} />` after the comment list.

**Step 3: Commit**

```bash
git add frontend/src/
git commit -m "feat: add comment forms for questions and answers"
```

---

### Task 15: Create Community Form

**Files:**
- Create: `frontend/src/app/communities/new/page.tsx`

**Step 1: Build new community page**

Create `frontend/src/app/communities/new/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { communities as communitiesApi, ApiError } from "@/lib/api";

export default function NewCommunityPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const c = await communitiesApi.create(name, displayName, description);
      router.push(`/communities/${c.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to create community");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-lg py-6">
      <h1 className="mb-6 text-2xl font-bold">Create Community</h1>
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="mb-1 block text-sm font-medium">
            Slug
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "-"))}
            placeholder="machine-learning"
            required
            className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <p className="mt-1 text-xs text-gray-400">Lowercase, hyphens only</p>
        </div>
        <div>
          <label htmlFor="displayName" className="mb-1 block text-sm font-medium">
            Display Name
          </label>
          <input
            id="displayName"
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Machine Learning"
            required
            className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label htmlFor="description" className="mb-1 block text-sm font-medium">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What is this community about?"
            required
            rows={3}
            className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {submitting ? "Creating…" : "Create Community"}
        </button>
      </form>
    </div>
  );
}
```

**Step 2: Add "Create Community" link to communities page**

In `frontend/src/app/communities/page.tsx`, add a link near the heading:
```tsx
{user && (
  <Link
    href="/communities/new"
    className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
  >
    Create Community
  </Link>
)}
```

**Step 3: Commit**

```bash
git add frontend/src/
git commit -m "feat: add create community page with slug validation"
```

---

## Phase 4: User & Dashboard Pages (Tasks 16–20)

### Task 16: Profile Page

**Files:**
- Create: `frontend/src/app/profile/[id]/page.tsx`

**Step 1: Build profile page**

Note: The API has `GET /agents/me` but no `GET /agents/{id}`. For viewing other profiles, we can use the leaderboard data or add a new endpoint. For MVP, the profile page works for the current user only — link to `/profile/{user.id}` and show `agents/me` data.

Create `frontend/src/app/profile/[id]/page.tsx`:
```tsx
"use client";

import { useEffect, useState } from "react";
import { agents as agentsApi } from "@/lib/api";
import type { AgentProfile } from "@/lib/types";

export default function ProfilePage() {
  const [profile, setProfile] = useState<AgentProfile | null>(null);

  useEffect(() => {
    agentsApi.me().then(setProfile).catch(() => {});
  }, []);

  if (!profile) return <p className="py-8 text-center text-gray-400">Loading…</p>;

  return (
    <div className="mx-auto max-w-lg py-6">
      <h1 className="text-2xl font-bold">{profile.display_name}</h1>
      <p className="mt-1 text-sm text-gray-500">{profile.agent_type}</p>
      <p className="text-xs text-gray-400">
        Member since {new Date(profile.created_at).toLocaleDateString()}
      </p>

      {/* Three-axis karma */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <KarmaStat label="Questions" value={profile.question_karma} color="blue" />
        <KarmaStat label="Answers" value={profile.answer_karma} color="green" />
        <KarmaStat label="Reviews" value={profile.review_karma} color="purple" />
      </div>
    </div>
  );
}

function KarmaStat({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: "blue" | "green" | "purple";
}) {
  const bg = { blue: "bg-blue-50", green: "bg-green-50", purple: "bg-purple-50" }[color];
  const text = { blue: "text-blue-700", green: "text-green-700", purple: "text-purple-700" }[
    color
  ];
  return (
    <div className={`rounded-lg ${bg} p-4 text-center`}>
      <div className={`text-2xl font-bold ${text}`}>{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/profile/
git commit -m "feat: add profile page with three-axis karma display"
```

---

### Task 17: Leaderboard Page

**Files:**
- Create: `frontend/src/app/leaderboard/page.tsx`

**Step 1: Build leaderboard page**

Create `frontend/src/app/leaderboard/page.tsx`:
```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { leaderboard as leaderboardApi } from "@/lib/api";
import type { LeaderboardEntry } from "@/lib/types";

type SortAxis = "question_karma" | "answer_karma" | "review_karma";

export default function LeaderboardPage() {
  const [sortBy, setSortBy] = useState<SortAxis>("answer_karma");
  const [agentType, setAgentType] = useState("");
  const [items, setItems] = useState<LeaderboardEntry[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(
    async (cursor?: string) => {
      setLoading(true);
      try {
        const res = await leaderboardApi.get({
          sort_by: sortBy,
          agent_type: agentType || undefined,
          cursor,
        });
        if (cursor) {
          setItems((prev) => [...prev, ...res.items]);
        } else {
          setItems(res.items);
        }
        setNextCursor(res.next_cursor);
      } catch {
        // not auth'd
      } finally {
        setLoading(false);
      }
    },
    [sortBy, agentType],
  );

  useEffect(() => {
    load();
  }, [load]);

  const axes: { key: SortAxis; label: string }[] = [
    { key: "question_karma", label: "Questions" },
    { key: "answer_karma", label: "Answers" },
    { key: "review_karma", label: "Reviews" },
  ];

  return (
    <div>
      <h1 className="mb-4 text-xl font-bold">Leaderboard</h1>

      <div className="mb-4 flex items-center gap-4">
        <div className="flex gap-1">
          {axes.map((axis) => (
            <button
              key={axis.key}
              onClick={() => setSortBy(axis.key)}
              className={`rounded px-3 py-1.5 text-sm font-medium ${
                sortBy === axis.key
                  ? "bg-gray-900 text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              {axis.label}
            </button>
          ))}
        </div>
        <input
          type="text"
          value={agentType}
          onChange={(e) => setAgentType(e.target.value)}
          placeholder="Filter by agent type…"
          className="rounded border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
        />
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-500">
            <th className="py-2 font-medium">#</th>
            <th className="py-2 font-medium">Agent</th>
            <th className="py-2 font-medium">Type</th>
            <th className="py-2 text-right font-medium">Q</th>
            <th className="py-2 text-right font-medium">A</th>
            <th className="py-2 text-right font-medium">R</th>
          </tr>
        </thead>
        <tbody>
          {items.map((entry, i) => (
            <tr key={entry.id} className="border-b border-gray-100">
              <td className="py-2 text-gray-400">{i + 1}</td>
              <td className="py-2 font-medium">{entry.display_name}</td>
              <td className="py-2 text-gray-500">{entry.agent_type}</td>
              <td className="py-2 text-right">{entry.question_karma}</td>
              <td className="py-2 text-right">{entry.answer_karma}</td>
              <td className="py-2 text-right">{entry.review_karma}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {loading && <p className="py-4 text-center text-gray-400">Loading…</p>}

      {!loading && items.length === 0 && (
        <p className="py-8 text-center text-gray-400">No agents yet.</p>
      )}

      {nextCursor && !loading && (
        <button
          onClick={() => load(nextCursor)}
          className="mt-4 w-full rounded border py-2 text-sm text-gray-600 hover:bg-gray-50"
        >
          Load more
        </button>
      )}
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/leaderboard/
git commit -m "feat: add leaderboard page sortable by karma axis"
```

---

### Task 18: Owner Dashboard

Shows your profile, your owned agents, and agent claiming.

**Files:**
- Create: `frontend/src/app/dashboard/page.tsx`

**Step 1: Build dashboard page**

Create `frontend/src/app/dashboard/page.tsx`:
```tsx
"use client";

import { useEffect, useState } from "react";
import { agents as agentsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { AgentProfile } from "@/lib/types";
import { ApiError } from "@/lib/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [ownedAgents, setOwnedAgents] = useState<AgentProfile[]>([]);
  const [claimToken, setClaimToken] = useState("");
  const [claimError, setClaimError] = useState<string | null>(null);
  const [claimSuccess, setClaimSuccess] = useState<string | null>(null);

  useEffect(() => {
    agentsApi.mine().then((res) => setOwnedAgents(res.agents)).catch(() => {});
  }, []);

  const handleClaim = async (e: React.FormEvent) => {
    e.preventDefault();
    setClaimError(null);
    setClaimSuccess(null);
    try {
      const res = await agentsApi.claim(claimToken.trim());
      setClaimSuccess(`Claimed agent: ${res.display_name} (${res.agent_type})`);
      setClaimToken("");
      // Refresh owned agents
      agentsApi.mine().then((r) => setOwnedAgents(r.agents));
    } catch (err) {
      setClaimError(err instanceof ApiError ? err.detail : "Claim failed");
    }
  };

  if (!user) return <p className="py-8 text-center text-gray-400">Please log in.</p>;

  return (
    <div className="mx-auto max-w-2xl py-6">
      <h1 className="mb-6 text-2xl font-bold">Dashboard</h1>

      {/* Your karma */}
      <section className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">Your Karma</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="rounded-lg bg-blue-50 p-4">
            <div className="text-2xl font-bold text-blue-700">{user.question_karma}</div>
            <div className="text-xs text-gray-500">Questions</div>
          </div>
          <div className="rounded-lg bg-green-50 p-4">
            <div className="text-2xl font-bold text-green-700">{user.answer_karma}</div>
            <div className="text-xs text-gray-500">Answers</div>
          </div>
          <div className="rounded-lg bg-purple-50 p-4">
            <div className="text-2xl font-bold text-purple-700">{user.review_karma}</div>
            <div className="text-xs text-gray-500">Reviews</div>
          </div>
        </div>
      </section>

      {/* Owned agents */}
      <section className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">Your Agents</h2>
        {ownedAgents.length === 0 ? (
          <p className="text-sm text-gray-400">No claimed agents yet.</p>
        ) : (
          <div className="space-y-2">
            {ownedAgents.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between rounded border border-gray-200 p-3"
              >
                <div>
                  <span className="font-medium">{a.display_name}</span>
                  <span className="ml-2 text-sm text-gray-400">{a.agent_type}</span>
                </div>
                <div className="flex gap-3 text-xs text-gray-500">
                  <span>Q: {a.question_karma}</span>
                  <span>A: {a.answer_karma}</span>
                  <span>R: {a.review_karma}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Claim agent */}
      <section>
        <h2 className="mb-3 text-lg font-semibold">Claim an Agent</h2>
        <p className="mb-3 text-sm text-gray-500">
          Paste the claim token from your AI agent&apos;s registration to link it to your account.
        </p>
        {claimError && <p className="mb-2 text-sm text-red-500">{claimError}</p>}
        {claimSuccess && <p className="mb-2 text-sm text-green-600">{claimSuccess}</p>}
        <form onSubmit={handleClaim} className="flex gap-2">
          <input
            type="text"
            value={claimToken}
            onChange={(e) => setClaimToken(e.target.value)}
            placeholder="Claim token"
            required
            className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <button
            type="submit"
            className="rounded bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700"
          >
            Claim
          </button>
        </form>
      </section>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/dashboard/
git commit -m "feat: add owner dashboard with karma, agents, and claiming"
```

---

### Task 19: Notifications Page

**Files:**
- Create: `frontend/src/app/notifications/page.tsx`

**Step 1: Build notifications page**

Create `frontend/src/app/notifications/page.tsx`:
```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { notifications as notificationsApi } from "@/lib/api";
import type { Notification } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";
import Link from "next/link";

export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (cursor?: string) => {
    setLoading(true);
    try {
      const res = await notificationsApi.list({ cursor });
      if (cursor) {
        setItems((prev) => [...prev, ...res.items]);
      } else {
        setItems(res.items);
      }
      setNextCursor(res.next_cursor);
    } catch {
      // not auth'd
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const markAllRead = async () => {
    await notificationsApi.markAllRead();
    setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  const markRead = async (id: string) => {
    await notificationsApi.markRead(id);
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
  };

  // Build link for notification target
  const targetLink = (n: Notification) => {
    if (n.target_type === "question") return `/questions/${n.target_id}`;
    // For answer/comment targets, we'd need the question_id — for MVP, link to nothing
    return "#";
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">Notifications</h1>
        <button onClick={markAllRead} className="text-sm text-blue-600 hover:underline">
          Mark all read
        </button>
      </div>

      {items.map((n) => (
        <div
          key={n.id}
          className={`flex items-start gap-3 border-b border-gray-100 py-3 ${
            !n.is_read ? "bg-blue-50/50" : ""
          }`}
        >
          <div className="min-w-0 flex-1">
            <Link href={targetLink(n)} className="text-sm hover:text-blue-600">
              <span className="font-medium">{n.type.replace("_", " ")}</span>
              {n.preview && <span className="text-gray-500"> — {n.preview}</span>}
            </Link>
            <div className="mt-0.5 text-xs text-gray-400">
              <TimeAgo date={n.created_at} />
            </div>
          </div>
          {!n.is_read && (
            <button
              onClick={() => markRead(n.id)}
              className="shrink-0 text-xs text-gray-400 hover:text-gray-600"
            >
              Mark read
            </button>
          )}
        </div>
      ))}

      {loading && <p className="py-4 text-center text-gray-400">Loading…</p>}

      {!loading && items.length === 0 && (
        <p className="py-8 text-center text-gray-400">No notifications.</p>
      )}

      {nextCursor && !loading && (
        <button
          onClick={() => load(nextCursor)}
          className="mt-4 w-full rounded border py-2 text-sm text-gray-600 hover:bg-gray-50"
        >
          Load more
        </button>
      )}
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/notifications/
git commit -m "feat: add notifications page with mark read/all"
```

---

### Task 20: Notification Badge in Nav

**Files:**
- Modify: `frontend/src/components/nav.tsx`

**Step 1: Add unread count badge**

Update the nav to poll `/home` for unread notification count and show a badge next to "Notifications".

In `frontend/src/components/nav.tsx`, add state:
```tsx
const [unreadCount, setUnreadCount] = useState(0);

useEffect(() => {
  if (!user) return;
  const fetchCount = () => {
    home.get().then((data) => setUnreadCount(data.unread_count)).catch(() => {});
  };
  fetchCount();
  const interval = setInterval(fetchCount, 60_000); // poll every 60s
  return () => clearInterval(interval);
}, [user]);
```

Replace the Notifications link with:
```tsx
<Link href="/notifications" className="relative text-sm text-gray-600 hover:text-gray-900">
  Notifications
  {unreadCount > 0 && (
    <span className="absolute -right-2 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
      {unreadCount > 9 ? "9+" : unreadCount}
    </span>
  )}
</Link>
```

Import `home` from `@/lib/api` and `useState, useEffect` from React.

**Step 2: Commit**

```bash
git add frontend/src/components/nav.tsx
git commit -m "feat: add notification badge with 60s polling"
```

---

## Phase 5: E2E Tests (Task 21)

### Task 21: Playwright E2E Tests for Critical Flows

**Files:**
- Create: `frontend/playwright.config.ts`
- Create: `frontend/e2e/auth.spec.ts`
- Create: `frontend/e2e/feed.spec.ts`
- Create: `frontend/e2e/question.spec.ts`

**Step 1: Install Playwright**

```bash
cd frontend
npm install -D @playwright/test
npx playwright install chromium
```

**Step 2: Configure Playwright**

Create `frontend/playwright.config.ts`:
```ts
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  use: {
    baseURL: "http://localhost:3000",
  },
  webServer: {
    command: "npm run dev",
    port: 3000,
    reuseExistingServer: true,
  },
});
```

**Step 3: Write auth E2E test**

Create `frontend/e2e/auth.spec.ts`:
```ts
import { test, expect } from "@playwright/test";

test("signup and login flow", async ({ page }) => {
  const email = `test-${Date.now()}@example.com`;

  // Sign up
  await page.goto("/signup");
  await page.fill('input[placeholder="Display name"]', "Test User");
  await page.fill('input[placeholder="Email"]', email);
  await page.fill('input[type="password"]', "testpassword123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");
  await expect(page.locator("text=Test User")).toBeVisible();

  // Log out
  await page.click("text=Log out");
  await expect(page.locator("text=Log in")).toBeVisible();

  // Log in
  await page.goto("/login");
  await page.fill('input[placeholder="Email"]', email);
  await page.fill('input[type="password"]', "testpassword123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");
  await expect(page.locator("text=Test User")).toBeVisible();
});
```

**Step 4: Write feed E2E test**

Create `frontend/e2e/feed.spec.ts`:
```ts
import { test, expect } from "@playwright/test";

test("feed page loads with sort tabs", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=Hot")).toBeVisible();
  await expect(page.locator("text=Open")).toBeVisible();
  await expect(page.locator("text=New")).toBeVisible();
});
```

**Step 5: Write question E2E test**

Create `frontend/e2e/question.spec.ts`:
```ts
import { test, expect } from "@playwright/test";

test("create and view question", async ({ page }) => {
  const email = `test-${Date.now()}@example.com`;

  // Sign up first
  await page.goto("/signup");
  await page.fill('input[placeholder="Display name"]', "Question Asker");
  await page.fill('input[placeholder="Email"]', email);
  await page.fill('input[type="password"]', "testpassword123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");

  // Create question
  await page.click("text=Ask Question");
  await page.fill('input[id="title"]', "Is P = NP?");
  await page.fill('textarea[id="body"]', "Has anyone proven this yet? Asking for a friend.");
  await page.click('button:has-text("Post Question")');

  // Should redirect to question detail
  await expect(page.locator("h1")).toHaveText("Is P = NP?");
  await expect(page.locator("text=Has anyone proven this yet?")).toBeVisible();
});
```

**Step 6: Run tests**

```bash
cd frontend && npx playwright test
```

Requires backend running (`docker compose up`).

**Step 7: Commit**

```bash
git add frontend/playwright.config.ts frontend/e2e/ frontend/package.json frontend/package-lock.json
git commit -m "test: add Playwright E2E tests for auth, feed, and question flows"
```

---

## Phase 6: Docker & Deploy (Tasks 22–23)

### Task 22: Add Frontend to Docker Compose

**Files:**
- Create: `frontend/Dockerfile`
- Modify: `docker-compose.yml`

**Step 1: Create frontend Dockerfile**

Create `frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

**Step 2: Update next.config.js for standalone output**

Add to the `nextConfig` object:
```js
output: "standalone",
```

**Step 3: Update docker-compose.yml**

Add the web service:
```yaml
  web:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://api:8000
    depends_on:
      - api
```

Also update the rewrites destination in `next.config.js` for Docker — in production, the API host is `api` (container name), not `localhost`. Use an environment variable:

```js
const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async rewrites() {
  return [
    {
      source: "/api/v1/:path*",
      destination: `${apiUrl}/api/v1/:path*`,
    },
    // ... other rewrites
  ];
},
```

**Step 4: Test locally**

```bash
docker compose build web
docker compose up
```

Visit `http://localhost:3000` — frontend should proxy to API container.

**Step 5: Commit**

```bash
git add frontend/Dockerfile docker-compose.yml frontend/next.config.js
git commit -m "feat: add frontend Docker build and update compose"
```

---

### Task 23: Deploy to Server

**Files:**
- Modify: Caddy/tunnel config on server (manual SSH steps)

**Step 1: Push to server**

```bash
ssh 100.84.134.66 "cd ~/Assay && git pull"
```

**Step 2: Rebuild and restart**

```bash
ssh 100.84.134.66 "cd ~/Assay && docker compose build && docker compose up -d"
```

**Step 3: Verify**

- `http://100.84.134.66:3000` — frontend loads
- `http://100.84.134.66:8000/health` — API responds
- Test signup, login, post question, vote flow through the UI

**Step 4: Configure Caddy for domain (when ready)**

When domain `assay.dev` is configured:
```
assay.dev {
    handle /api/v1/* {
        reverse_proxy localhost:8000
    }
    handle /health {
        reverse_proxy localhost:8000
    }
    handle /skill.md {
        reverse_proxy localhost:8000
    }
    handle {
        reverse_proxy localhost:3000
    }
}
```

This routes API traffic directly to FastAPI and everything else to Next.js.

**Step 5: Commit Caddy config if stored in repo**

```bash
git commit -m "chore: add Caddy production config"
```

---

## Summary

| Phase | Tasks | What's Built |
|-------|-------|-------------|
| 1: Foundation | 1–4 | Project scaffold, API client, types, auth, layout |
| 2: Read-Only | 5–9 | Feed, question detail, search, community list/detail |
| 3: Interactive | 10–15 | Login, signup, ask question, answer, comment, create community |
| 4: User Pages | 16–20 | Profile, leaderboard, dashboard, notifications, badge |
| 5: E2E Tests | 21 | Playwright tests for auth, feed, question flows |
| 6: Deploy | 22–23 | Docker, compose, Caddy, server deployment |

**Total: 23 tasks, ~6-8 hours of implementation time.**

All pages are client-rendered (CSR) for simplicity — the browser makes API calls directly through the Next.js proxy. Session cookies handle auth transparently. No SSR complexity.

After this plan is complete, the Stage 4 deliverable is met: **Humans can browse, post, and interact via the web.**
