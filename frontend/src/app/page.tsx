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

      {expandedId && previewCache[expandedId] && (
        <QuestionOverlay
          preview={previewCache[expandedId]}
          onClose={closeOverlay}
        />
      )}

      {expandedId && previewLoadingId === expandedId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <p className="text-xtext-secondary">Loading...</p>
        </div>
      )}
    </div>
  );
}
