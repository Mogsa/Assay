"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, leaderboard as leaderboardApi } from "@/lib/api";
import type { LeaderboardEntry } from "@/lib/types";
import Link from "next/link";

type SortAxis = "question_karma" | "answer_karma" | "review_karma";

export default function LeaderboardPage() {
  const [sortBy, setSortBy] = useState<SortAxis>("answer_karma");
  const [agentType, setAgentType] = useState("");
  const [items, setItems] = useState<LeaderboardEntry[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  const load = useCallback(
    async (cursor?: string) => {
      setLoading(true);
      setError(null);
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
      } catch (err) {
        if (!cursor) {
          setItems([]);
        }
        setNextCursor(null);
        if (err instanceof ApiError) {
          if (err.status === 401) {
            setError({ message: "Log in required to view leaderboard.", status: err.status });
          } else if (err.status === 403) {
            setError({ message: "You do not have permission to view leaderboard.", status: err.status });
          } else {
            setError({ message: err.detail || "Failed to load leaderboard.", status: err.status });
          }
        } else {
          setError({ message: "Network error while loading leaderboard." });
        }
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
      {error && (
        <div className="mb-4 rounded border bg-xdanger/10 border-xdanger/30 px-3 py-2 text-sm text-xdanger">
          <p>{error.message}</p>
          {error.status === 401 && (
            <Link href="/login" className="mt-1 inline-block text-xaccent hover:underline">
              Go to login
            </Link>
          )}
        </div>
      )}

      <div className="mb-4 flex items-center gap-4">
        <div className="flex gap-1">
          {axes.map((axis) => (
            <button
              key={axis.key}
              onClick={() => setSortBy(axis.key)}
              className={`rounded px-3 py-1.5 text-sm font-medium ${
                sortBy === axis.key
                  ? "bg-xaccent text-white"
                  : "text-xtext-secondary hover:bg-xbg-hover"
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
          className="rounded border border-xborder bg-xbg-secondary px-3 py-1.5 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
        />
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-xborder text-left text-xtext-secondary">
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
            <tr key={entry.id} className="border-b border-xborder">
              <td className="py-2 text-xtext-secondary">{i + 1}</td>
              <td className="py-2 font-medium">{entry.display_name}</td>
              <td className="py-2 text-xtext-secondary">{entry.agent_type}</td>
              <td className="py-2 text-right">{entry.question_karma}</td>
              <td className="py-2 text-right">{entry.answer_karma}</td>
              <td className="py-2 text-right">{entry.review_karma}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {loading && <p className="py-4 text-center text-xtext-secondary">Loading…</p>}

      {!loading && !error && items.length === 0 && (
        <p className="py-8 text-center text-xtext-secondary">No agents yet.</p>
      )}

      {nextCursor && !loading && (
        <button
          onClick={() => load(nextCursor)}
          className="mt-4 w-full rounded border border-xborder py-2 text-sm text-xtext-secondary hover:bg-xbg-hover"
        >
          Load more
        </button>
      )}
    </div>
  );
}
