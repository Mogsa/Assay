"use client";

import { useEffect, useState } from "react";
import { communities as communitiesApi } from "@/lib/api";
import type { Community } from "@/lib/types";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function CommunitiesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<Community[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async (cursor?: string) => {
    setLoading(true);
    try {
      const res = await communitiesApi.list(cursor);
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
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
          >
            Create Community
          </Link>
        )}
      </div>
      <div className="space-y-3">
        {items.map((c) => (
          <Link
            key={c.id}
            href={`/communities/${c.id}`}
            className="block rounded border border-gray-200 p-4 hover:bg-gray-50"
          >
            <div className="flex items-baseline justify-between">
              <h2 className="font-medium">{c.display_name}</h2>
              <span className="text-sm text-gray-400">{c.member_count} members</span>
            </div>
            <p className="mt-1 text-sm text-gray-500">{c.description}</p>
          </Link>
        ))}
      </div>

      {loading && <p className="py-8 text-center text-gray-400">Loading…</p>}

      {!loading && items.length === 0 && (
        <p className="py-8 text-center text-gray-400">No communities yet.</p>
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
