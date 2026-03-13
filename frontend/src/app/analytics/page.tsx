"use client";

import { useState, useEffect } from "react";
import { analytics } from "@/lib/api";
import { GraphResponse, FrontierResponse } from "@/lib/types";
import ConnectionsView from "@/components/knowledge-graph/connections-view";
import FrontierMap from "@/components/knowledge-graph/frontier-map";

type Tab = "connections" | "frontier";

export default function AnalyticsPage() {
  const [tab, setTab] = useState<Tab>("connections");
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [frontierData, setFrontierData] = useState<FrontierResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [graph, frontier] = await Promise.all([
          analytics.graph(),
          analytics.frontier(),
        ]);
        setGraphData(graph);
        setFrontierData(frontier);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load graph data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (error) return <div className="p-8 text-red-400">{error}</div>;
  if (loading || !graphData) return <div className="p-8 text-gray-500">Loading graph...</div>;

  return (
    <div className="flex flex-col h-full">
      {/* Header with tabs */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-800">
        <h1 className="text-lg font-semibold">Knowledge Graph</h1>
        <div className="flex gap-1">
          <button
            onClick={() => setTab("connections")}
            className={`px-3 py-1.5 text-sm rounded-md ${tab === "connections" ? "bg-gray-800 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >
            Connections
          </button>
          <button
            onClick={() => setTab("frontier")}
            className={`px-3 py-1.5 text-sm rounded-md ${tab === "frontier" ? "bg-gray-800 text-white" : "text-gray-500 hover:text-gray-300"}`}
          >
            Frontier Map
          </button>
        </div>
      </div>

      {/* Graph view */}
      <div className="flex-1 overflow-hidden">
        {tab === "connections" && <ConnectionsView data={graphData} />}
        {tab === "frontier" && <FrontierMap data={graphData} frontier={frontierData!} />}
      </div>
    </div>
  );
}
