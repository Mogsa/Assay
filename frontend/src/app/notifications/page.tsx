"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, notifications as notificationsApi } from "@/lib/api";
import type { Notification } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";
import Link from "next/link";

export default function NotificationsPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  const load = useCallback(async (cursor?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await notificationsApi.list({ cursor });
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
          setError({ message: "Log in required to view notifications.", status: err.status });
        } else if (err.status === 403) {
          setError({ message: "You do not have permission to view notifications.", status: err.status });
        } else {
          setError({ message: err.detail || "Failed to load notifications.", status: err.status });
        }
      } else {
        setError({ message: "Network error while loading notifications." });
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const markAllRead = async () => {
    try {
      await notificationsApi.markAllRead();
      setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      if (err instanceof ApiError) {
        setError({ message: err.detail || "Failed to mark notifications read.", status: err.status });
      } else {
        setError({ message: "Network error while updating notifications." });
      }
    }
  };

  const markRead = async (id: string) => {
    try {
      await notificationsApi.markRead(id);
      setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch (err) {
      if (err instanceof ApiError) {
        setError({ message: err.detail || "Failed to mark notification read.", status: err.status });
      } else {
        setError({ message: "Network error while updating notifications." });
      }
    }
  };

  const targetLink = (n: Notification) => {
    if (n.target_type === "question") return `/questions/${n.target_id}`;
    return "#";
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">Notifications</h1>
        <button onClick={markAllRead} className="text-sm text-xaccent hover:underline">
          Mark all read
        </button>
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

      {items.map((n) => (
        <div
          key={n.id}
          className={`flex items-start gap-3 border-b border-xborder py-3 ${
            !n.is_read ? "bg-xaccent/5" : ""
          }`}
        >
          <div className="min-w-0 flex-1">
            <Link href={targetLink(n)} className="text-sm hover:text-xaccent">
              <span className="font-medium">{n.type.replace(/_/g, " ")}</span>
              {n.preview && <span className="text-xtext-secondary"> — {n.preview}</span>}
            </Link>
            <div className="mt-0.5 text-xs text-xtext-secondary">
              <TimeAgo date={n.created_at} />
            </div>
          </div>
          {!n.is_read && (
            <button
              onClick={() => markRead(n.id)}
              className="shrink-0 text-xs text-xtext-secondary hover:text-xtext-primary"
            >
              Mark read
            </button>
          )}
        </div>
      ))}

      {loading && <p className="py-4 text-center text-xtext-secondary">Loading…</p>}

      {!loading && !error && items.length === 0 && (
        <p className="py-8 text-center text-xtext-secondary">No notifications.</p>
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
