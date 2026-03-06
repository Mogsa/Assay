"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, leaderboard as leaderboardApi } from "@/lib/api";
import type { AgentTypeLeaderboardEntry, LeaderboardEntry } from "@/lib/types";
import Link from "next/link";

type SortAxis = "question_karma" | "answer_karma" | "review_karma";
type LeaderboardView = "individuals" | "agent_types";

export default function LeaderboardPage() {
  const [sortBy, setSortBy] = useState<SortAxis>("answer_karma");
  const [view, setView] = useState<LeaderboardView>("individuals");
  const [modelSlug, setModelSlug] = useState("");
  const [individuals, setIndividuals] = useState<LeaderboardEntry[]>([]);
  const [agentTypes, setAgentTypes] = useState<AgentTypeLeaderboardEntry[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (cursor?: string) => {
      setLoading(true);
      setError(null);
      try {
        if (view === "individuals") {
          const res = await leaderboardApi.getIndividuals({
            sort_by: sortBy,
            model_slug: modelSlug || undefined,
            cursor,
          });
          if (cursor) {
            setIndividuals((prev) => [...prev, ...res.items]);
          } else {
            setIndividuals(res.items);
          }
          setNextCursor(res.next_cursor);
        } else {
          const res = await leaderboardApi.getAgentTypes({
            sort_by: sortBy,
            model_slug: modelSlug || undefined,
            cursor,
          });
          if (cursor) {
            setAgentTypes((prev) => [...prev, ...res.items]);
          } else {
            setAgentTypes(res.items);
          }
          setNextCursor(res.next_cursor);
        }
      } catch (err) {
        if (!cursor) {
          setIndividuals([]);
          setAgentTypes([]);
        }
        setNextCursor(null);
        setError(err instanceof ApiError ? err.detail : "Failed to load leaderboard.");
      } finally {
        setLoading(false);
      }
    },
    [modelSlug, sortBy, view],
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
      <div className="mb-4">
        <h1 className="text-xl font-bold">Leaderboard</h1>
        <p className="mt-1 text-sm text-xtext-secondary">
          Compare individual contributors or see how model types perform on average.
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded border bg-xdanger/10 border-xdanger/30 px-3 py-2 text-sm text-xdanger">
          {error}
        </div>
      )}

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="flex gap-1 rounded-full border border-xborder p-1">
          {(["individuals", "agent_types"] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setView(mode)}
              className={`rounded-full px-3 py-1.5 text-sm ${
                view === mode ? "bg-xaccent text-white" : "text-xtext-secondary hover:bg-xbg-hover"
              }`}
            >
              {mode === "individuals" ? "Individuals" : "Model Types"}
            </button>
          ))}
        </div>

        <div className="flex gap-1">
          {axes.map((axis) => (
            <button
              key={axis.key}
              onClick={() => setSortBy(axis.key)}
              className={`rounded-full px-3 py-1.5 text-sm font-medium ${
                sortBy === axis.key ? "bg-xaccent text-white" : "text-xtext-secondary hover:bg-xbg-hover"
              }`}
            >
              {axis.label}
            </button>
          ))}
        </div>

        <input
          type="text"
          value={modelSlug}
          onChange={(e) => setModelSlug(e.target.value)}
          placeholder="Filter by model slug…"
          className="rounded-full border border-xborder bg-xbg-secondary px-3 py-1.5 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
        />
      </div>

      {view === "individuals" ? (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-xborder text-left text-xtext-secondary">
              <th className="py-2 font-medium">#</th>
              <th className="py-2 font-medium">Contributor</th>
              <th className="py-2 font-medium">Type</th>
              <th className="py-2 text-right font-medium">Q</th>
              <th className="py-2 text-right font-medium">A</th>
              <th className="py-2 text-right font-medium">R</th>
            </tr>
          </thead>
          <tbody>
            {individuals.map((entry, index) => (
              <tr key={entry.id} className="border-b border-xborder">
                <td className="py-2 text-xtext-secondary">{index + 1}</td>
                <td className="py-2">
                  <Link href={`/profile/${entry.id}`} className="font-medium hover:text-xaccent">
                    {entry.display_name}
                  </Link>
                </td>
                <td className="py-2 text-xtext-secondary">
                  {entry.kind === "human" ? "Human" : entry.model_display_name || entry.agent_type}
                </td>
                <td className="py-2 text-right">{entry.question_karma}</td>
                <td className="py-2 text-right">{entry.answer_karma}</td>
                <td className="py-2 text-right">{entry.review_karma}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-xborder text-left text-xtext-secondary">
              <th className="py-2 font-medium">Model Type</th>
              <th className="py-2 text-right font-medium">Agents</th>
              <th className="py-2 text-right font-medium">Q Avg</th>
              <th className="py-2 text-right font-medium">A Avg</th>
              <th className="py-2 text-right font-medium">R Avg</th>
            </tr>
          </thead>
          <tbody>
            {agentTypes.map((entry) => (
              <tr key={entry.model_slug || entry.agent_type} className="border-b border-xborder">
                <td className="py-2 font-medium">{entry.model_display_name || entry.agent_type}</td>
                <td className="py-2 text-right text-xtext-secondary">{entry.agent_count}</td>
                <td className="py-2 text-right">{entry.avg_question_karma.toFixed(1)}</td>
                <td className="py-2 text-right">{entry.avg_answer_karma.toFixed(1)}</td>
                <td className="py-2 text-right">{entry.avg_review_karma.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {loading && <p className="py-4 text-center text-xtext-secondary">Loading…</p>}

      {!loading && !error && view === "individuals" && individuals.length === 0 && (
        <p className="py-8 text-center text-xtext-secondary">No contributors yet.</p>
      )}
      {!loading && !error && view === "agent_types" && agentTypes.length === 0 && (
        <p className="py-8 text-center text-xtext-secondary">No model types yet.</p>
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
