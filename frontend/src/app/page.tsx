"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, questions as questionsApi } from "@/lib/api";
import type { QuestionSummary } from "@/lib/types";
import { FeedCard } from "@/components/feed/feed-card";
import Link from "next/link";
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
