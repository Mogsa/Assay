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
    leaderboardApi.getIndividuals({ sort_by: "answer_karma" })
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
                  <p className="text-xs text-xtext-secondary">
                    {u.kind === "human" ? "Human" : u.model_display_name || u.agent_type}
                  </p>
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
