"use client";

import { useEffect, useState } from "react";
import { ApiError, communities as communitiesApi } from "@/lib/api";
import type { Community } from "@/lib/types";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function CommunitiesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<Community[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  const load = async (cursor?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await communitiesApi.list(cursor);
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
          setError({ message: "Log in required to view communities.", status: err.status });
        } else if (err.status === 403) {
          setError({ message: "You do not have permission to view communities.", status: err.status });
        } else {
          setError({ message: err.detail || "Failed to load communities.", status: err.status });
        }
      } else {
        setError({ message: "Network error while loading communities." });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">Communities</h1>
        {user && (
          <Link
            href="/communities/new"
            className="rounded bg-xaccent px-4 py-2 text-sm font-medium text-white hover:bg-xaccent-hover"
          >
            Create Community
          </Link>
        )}
      </div>
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
      <div className="space-y-3">
        {items.map((c) => (
          <Link
            key={c.id}
            href={`/communities/${c.id}`}
            className="block rounded border border-xborder p-4 hover:bg-xbg-hover"
          >
            <div className="flex items-baseline justify-between">
              <h2 className="font-medium">{c.display_name}</h2>
              <span className="text-sm text-xtext-secondary">{c.member_count} members</span>
            </div>
            <p className="mt-1 text-sm text-xtext-secondary">{c.description}</p>
          </Link>
        ))}
      </div>

      {loading && <p className="py-8 text-center text-xtext-secondary">Loading…</p>}

      {!loading && !error && items.length === 0 && (
        <p className="py-8 text-center text-xtext-secondary">No communities yet.</p>
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
