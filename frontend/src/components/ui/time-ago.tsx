"use client";

import { useEffect, useState } from "react";

export function TimeAgo({ date }: { date: string }) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 60_000);
    return () => clearInterval(interval);
  }, []);

  const seconds = Math.floor((now - new Date(date).getTime()) / 1000);
  if (seconds < 60) return <span>{seconds}s ago</span>;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return <span>{minutes}m ago</span>;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return <span>{hours}h ago</span>;
  const days = Math.floor(hours / 24);
  return <span>{days}d ago</span>;
}
