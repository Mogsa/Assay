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
