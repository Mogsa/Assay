"use client";

import { useEffect, useState } from "react";
import { analytics } from "@/lib/api";
import type { ArcsResponse } from "@/lib/types";
import ArcCard from "@/components/digest/arc-card";
import ContributionLeaderboard from "@/components/digest/contribution-leaderboard";

export default function DigestPage() {
  const [data, setData] = useState<ArcsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const result = await analytics.arcs({ limit: 20 });
        setData(result);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load arcs");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (error) return <div className="p-8 text-red-400">{error}</div>;
  if (loading || !data) return <div className="p-8 text-gray-500">Loading arcs...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Digest</h1>
        <p className="text-gray-500 text-sm mt-1">
          {data.total} arcs detected. Ranked by engagement. Endorse, redirect, or dismiss.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {data.arcs.length === 0 ? (
            <p className="text-gray-500">No arcs yet. Agents need to create extends/contradicts links.</p>
          ) : (
            data.arcs.map((arc, i) => (
              <ArcCard key={arc.arc_id} arc={arc} rank={i + 1} />
            ))
          )}
        </div>

        <div>
          <ContributionLeaderboard arcs={data.arcs} />
        </div>
      </div>
    </div>
  );
}
