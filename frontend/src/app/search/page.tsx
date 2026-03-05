"use client";

import { useState } from "react";
import { ApiError, search } from "@/lib/api";
import type { QuestionSummary } from "@/lib/types";
import { QuestionCard } from "@/components/questions/question-card";
import Link from "next/link";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<QuestionSummary[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  const doSearch = async (cursor?: string) => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await search.query(query, cursor);
      if (cursor) {
        setResults((prev) => [...prev, ...res.items]);
      } else {
        setResults(res.items);
      }
      setNextCursor(res.next_cursor);
      setSearched(true);
    } catch (err) {
      if (!cursor) {
        setResults([]);
      }
      setNextCursor(null);
      setSearched(true);
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError({ message: "Log in required to search questions.", status: err.status });
        } else if (err.status === 403) {
          setError({ message: "You do not have permission to search.", status: err.status });
        } else {
          setError({ message: err.detail || "Search failed.", status: err.status });
        }
      } else {
        setError({ message: "Network error while searching." });
      }
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
          className="flex-1 rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded bg-xaccent px-4 py-2 text-sm font-medium text-white hover:bg-xaccent-hover"
        >
          Search
        </button>
      </form>
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

      {results.map((q) => (
        <QuestionCard key={q.id} question={q} />
      ))}

      {searched && !error && results.length === 0 && !loading && (
        <p className="py-8 text-center text-xtext-secondary">No results found.</p>
      )}

      {nextCursor && (
        <button
          onClick={() => doSearch(nextCursor)}
          className="mt-4 w-full rounded border border-xborder py-2 text-sm text-xtext-secondary hover:bg-xbg-hover"
        >
          Load more
        </button>
      )}
    </div>
  );
}
