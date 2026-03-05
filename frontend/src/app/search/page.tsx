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
