"use client";
import { GraphResponse, FrontierResponse, GraphFilterState, FrontierStatus, GraphNode } from "@/lib/types";

const STATUS_COLORS: Record<FrontierStatus, string> = {
  frontier: "#6f6fd0",
  debated: "#d06f6f",
  resolved: "#4aad4a",
  explored: "#555",
  isolated: "#333",
};

const EDGE_COLORS: Record<string, string> = {
  extends: "#6f6fd0",
  contradicts: "#d06f6f",
  references: "#6fd06f",
};

interface Props {
  data: GraphResponse;
  frontier: FrontierResponse | null;
  filters: GraphFilterState;
  onFiltersChange: (filters: GraphFilterState) => void;
  classifyNode: (node: GraphNode) => FrontierStatus;
}

export default function GraphSidebar({ data, filters, onFiltersChange, classifyNode }: Props) {
  const questions = data.nodes.filter(n => n.type === "question");

  // Count statuses
  const statusCounts: Record<FrontierStatus, number> = {
    frontier: 0, debated: 0, resolved: 0, explored: 0, isolated: 0,
  };
  for (const q of questions) {
    statusCounts[classifyNode(q)]++;
  }

  // Count edge types (non-structural only)
  const edgeCounts: Record<string, number> = {};
  for (const edge of data.edges) {
    if (edge.edge_type !== "structural") {
      edgeCounts[edge.edge_type] = (edgeCounts[edge.edge_type] || 0) + 1;
    }
  }

  const toggle = (key: keyof GraphFilterState) => {
    onFiltersChange({ ...filters, [key]: !filters[key as keyof GraphFilterState] });
  };

  const statusFilters: { key: keyof GraphFilterState; label: string; status: FrontierStatus }[] = [
    { key: "showFrontier", label: "Frontier", status: "frontier" },
    { key: "showDebated", label: "Debated", status: "debated" },
    { key: "showResolved", label: "Resolved", status: "resolved" },
    { key: "showExplored", label: "Explored", status: "explored" },
    { key: "showIsolated", label: "Isolated", status: "isolated" },
  ];

  const linkFilters: { key: keyof GraphFilterState; label: string; type: string }[] = [
    { key: "showExtends", label: "extends", type: "extends" },
    { key: "showContradicts", label: "contradicts", type: "contradicts" },
    { key: "showReferences", label: "references", type: "references" },
  ];

  return (
    <div className="w-[260px] border-r border-gray-800 bg-gray-950 overflow-y-auto p-4 flex flex-col gap-5">
      {/* Overview stats */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Overview</h3>
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">{questions.length}</div>
            <div className="text-[10px] text-gray-500">Questions</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">
              {data.edges.filter(e => e.edge_type !== "structural").length}
            </div>
            <div className="text-[10px] text-gray-500">Links</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">{data.communities.length}</div>
            <div className="text-[10px] text-gray-500">Communities</div>
          </div>
        </div>
      </div>

      {/* Status filters */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Status</h3>
        <div className="flex flex-col gap-1.5">
          {statusFilters.map(({ key, label, status }) => (
            <label key={key} className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
              <input
                type="checkbox"
                checked={filters[key] as boolean}
                onChange={() => toggle(key)}
                className="rounded"
              />
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: STATUS_COLORS[status] }} />
              {label} ({statusCounts[status]})
            </label>
          ))}
        </div>
      </div>

      {/* Quick views */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Quick Views</h3>
        <div className="flex flex-col gap-1.5">
          <button
            onClick={() => onFiltersChange({
              ...filters,
              showFrontier: true, showDebated: true,
              showResolved: false, showExplored: false, showIsolated: false,
            })}
            className="text-left text-xs px-2 py-1.5 rounded bg-gray-900 border border-gray-800 text-gray-400 hover:text-gray-200 hover:border-gray-700"
          >
            Show only frontier + debated
          </button>
          <button
            onClick={() => onFiltersChange({
              ...filters,
              showFrontier: true, showDebated: true,
              showResolved: true, showExplored: true, showIsolated: true,
            })}
            className="text-left text-xs px-2 py-1.5 rounded bg-gray-900 border border-gray-800 text-gray-400 hover:text-gray-200 hover:border-gray-700"
          >
            Show all
          </button>
        </div>
      </div>

      {/* Link type filters */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Link Types</h3>
        <div className="flex flex-col gap-1.5">
          {linkFilters.map(({ key, label, type }) => (
            <label key={key} className="flex items-center justify-between text-xs text-gray-400 cursor-pointer">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={filters[key] as boolean}
                  onChange={() => toggle(key)}
                  className="rounded"
                />
                <span className="w-3 h-0.5 rounded" style={{ background: EDGE_COLORS[type] || "#555" }} />
                {label}
              </div>
              <span className="text-gray-600">{edgeCounts[type] || 0}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Communities list */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">
          Communities ({data.communities.length})
        </h3>
        <div className="flex flex-col gap-1.5">
          {filters.view === "community" && (
            <button
              onClick={() => onFiltersChange({ ...filters, view: "overview", selectedCommunityId: null })}
              className="text-left text-xs text-blue-400 hover:text-blue-300 mb-1"
            >
              ← All Communities
            </button>
          )}
          {data.communities.map(community => {
            const count = questions.filter(q => q.community_id === community.id).length;
            return (
              <button
                key={community.id}
                onClick={() => onFiltersChange({
                  ...filters,
                  view: "community",
                  selectedCommunityId: community.id,
                })}
                className={`text-left text-xs px-2 py-1 rounded flex justify-between ${
                  filters.selectedCommunityId === community.id
                    ? "bg-gray-800 text-gray-200"
                    : "text-gray-400 hover:text-gray-300 hover:bg-gray-900"
                }`}
              >
                <span className="truncate">{community.name}</span>
                <span className="text-gray-600 ml-2">{count}</span>
              </button>
            );
          })}
          {(() => {
            const uncatCount = questions.filter(q => !q.community_id).length;
            if (uncatCount === 0) return null;
            return (
              <button
                onClick={() => onFiltersChange({
                  ...filters,
                  view: "community",
                  selectedCommunityId: "__uncategorized__",
                })}
                className={`text-left text-xs px-2 py-1 rounded flex justify-between ${
                  filters.selectedCommunityId === "__uncategorized__"
                    ? "bg-gray-800 text-gray-200"
                    : "text-gray-400 hover:text-gray-300 hover:bg-gray-900"
                }`}
              >
                <span className="truncate italic">Uncategorized</span>
                <span className="text-gray-600 ml-2">{uncatCount}</span>
              </button>
            );
          })()}
        </div>
      </div>

      {/* Agents (drill-down only) */}
      {filters.view === "community" && (
        <div>
          <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Agents ({data.agents.length})</h3>
          <div className="flex flex-col gap-1.5">
            {data.agents.map((agent, i) => {
              const palette = ["#4aad4a", "#ad4a4a", "#4a4aad", "#d0ad6f", "#4aadad", "#ad4aad"];
              return (
                <div key={agent.id} className="flex items-center gap-2 text-xs text-gray-400">
                  <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: palette[i % palette.length] }} />
                  <span className="truncate">{agent.display_name}</span>
                  <span className="text-gray-600 ml-auto">{agent.kind}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
