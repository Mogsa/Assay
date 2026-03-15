"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { analytics } from "@/lib/api";
import {
  GraphResponse, FrontierResponse, GraphNode, GraphFilterState,
  DEFAULT_FILTERS, FrontierStatus
} from "@/lib/types";
import ConnectionsView, { classifyNode } from "@/components/knowledge-graph/connections-view";
import GraphSidebar from "@/components/knowledge-graph/graph-sidebar";
import DetailPanel from "@/components/knowledge-graph/detail-panel";

export default function AnalyticsPage() {
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [frontierData, setFrontierData] = useState<FrontierResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<GraphFilterState>(DEFAULT_FILTERS);

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
        setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const { frontierIds, debateIds, isolatedIds } = useMemo(() => ({
    frontierIds: new Set(frontierData?.frontier_questions.map(q => q.id) ?? []),
    debateIds: new Set(frontierData?.active_debates.map(d => d.question_id) ?? []),
    isolatedIds: new Set(frontierData?.isolated_questions.map(q => q.id) ?? []),
  }), [frontierData]);

  const classify = useCallback((node: GraphNode): FrontierStatus => {
    return classifyNode(node, frontierIds, debateIds, isolatedIds);
  }, [frontierIds, debateIds, isolatedIds]);

  const selectedNode = graphData?.nodes.find(n => n.id === filters.selectedNodeId) ?? null;

  if (error) return <div className="p-8 text-red-400">{error}</div>;
  if (loading || !graphData) return <div className="p-8 text-gray-500">Loading graph...</div>;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center px-5 py-3 border-b border-gray-800">
        <h1 className="text-lg font-semibold">Knowledge Graph</h1>
      </div>
      <div className="flex flex-1 overflow-hidden">
        <GraphSidebar
          data={graphData}
          frontier={frontierData}
          filters={filters}
          onFiltersChange={setFilters}
          classifyNode={classify}
        />
        <div className="flex-1 overflow-hidden">
          <ConnectionsView
            data={graphData}
            frontier={frontierData}
            filters={filters}
            onSelectNode={(node) => setFilters(f => ({ ...f, selectedNodeId: node?.id ?? null }))}
            onSelectCommunity={(cid) => setFilters(f => ({
              ...f,
              view: cid ? "community" : "overview",
              selectedCommunityId: cid || null,
            }))}
          />
        </div>
        {selectedNode && (
          <DetailPanel
            node={selectedNode}
            data={graphData}
            onClose={() => setFilters(f => ({ ...f, selectedNodeId: null }))}
          />
        )}
      </div>
    </div>
  );
}
