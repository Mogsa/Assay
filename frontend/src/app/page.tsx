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
        // Not auth'd or no questions
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
