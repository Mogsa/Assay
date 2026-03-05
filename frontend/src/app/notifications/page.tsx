"use client";

import { useCallback, useEffect, useState } from "react";
import { notifications as notificationsApi } from "@/lib/api";
import type { Notification } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";
import Link from "next/link";

export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (cursor?: string) => {
    setLoading(true);
    try {
      const res = await notificationsApi.list({ cursor });
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
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const markAllRead = async () => {
    await notificationsApi.markAllRead();
    setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  const markRead = async (id: string) => {
    await notificationsApi.markRead(id);
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
  };

  const targetLink = (n: Notification) => {
    if (n.target_type === "question") return `/questions/${n.target_id}`;
    return "#";
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">Notifications</h1>
        <button onClick={markAllRead} className="text-sm text-blue-600 hover:underline">
          Mark all read
        </button>
      </div>

      {items.map((n) => (
        <div
          key={n.id}
          className={`flex items-start gap-3 border-b border-gray-100 py-3 ${
            !n.is_read ? "bg-blue-50/50" : ""
          }`}
        >
          <div className="min-w-0 flex-1">
            <Link href={targetLink(n)} className="text-sm hover:text-blue-600">
              <span className="font-medium">{n.type.replace(/_/g, " ")}</span>
              {n.preview && <span className="text-gray-500"> — {n.preview}</span>}
            </Link>
            <div className="mt-0.5 text-xs text-gray-400">
              <TimeAgo date={n.created_at} />
            </div>
          </div>
          {!n.is_read && (
            <button
              onClick={() => markRead(n.id)}
              className="shrink-0 text-xs text-gray-400 hover:text-gray-600"
            >
              Mark read
            </button>
          )}
        </div>
      ))}

      {loading && <p className="py-4 text-center text-gray-400">Loading…</p>}

      {!loading && items.length === 0 && (
        <p className="py-8 text-center text-gray-400">No notifications.</p>
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
