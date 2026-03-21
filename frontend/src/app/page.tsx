"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, questions as questionsApi } from "@/lib/api";
import type { QuestionFeedPreview, QuestionScanSummary } from "@/lib/types";
import { FeedCard } from "@/components/feed/feed-card";

type SortMode = "hot" | "best_questions" | "best_answers" | "new";

const TABS: { key: SortMode; label: string }[] = [
  { key: "hot", label: "Hot" },
  { key: "best_questions", label: "Best Questions" },
  { key: "best_answers", label: "Best Answers" },
  { key: "new", label: "New" },
];

export default function FeedPage() {
  const [sort, setSort] = useState<SortMode>("hot");
  const [items, setItems] = useState<QuestionScanSummary[]>([]);
  const [previews, setPreviews] = useState<Record<string, QuestionFeedPreview>>({});
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  const loadPreviews = useCallback(async (questionIds: string[]) => {
    const results = await Promise.allSettled(
      questionIds.map((id) => questionsApi.preview(id))
    );
    setPreviews((prev) => {
      const next = { ...prev };
      results.forEach((result, i) => {
        if (result.status === "fulfilled") {
          next[questionIds[i]] = result.value;
        }
      });
      return next;
    });
  }, []);

  const load = useCallback(
    async (cursor?: string) => {
      setLoading(true);
      setError(null);
      try {
        const res = await questionsApi.listScan({ sort, cursor });
        if (cursor) {
          setItems((prev) => [...prev, ...res.items]);
        } else {
          setItems(res.items);
          setPreviews({});
        }
        setNextCursor(res.next_cursor);
        // Load previews for new items
        const newIds = res.items.map((q) => q.id);
        loadPreviews(newIds);
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
    [sort, loadPreviews],
  );

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="mx-auto max-w-[900px]">
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
          preview={previews[q.id]}
        />
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
