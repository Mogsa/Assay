"use client";
import { GraphNode, GraphResponse } from "@/lib/types";

interface Props {
  node: GraphNode;
  data: GraphResponse;
  onClose: () => void;
}

export default function DetailPanel({ node, data, onClose }: Props) {
  // Find connected edges
  const connectedEdges = data.edges.filter(
    e => e.source === node.id || e.target === node.id
  );

  // Find connected nodes
  const connectedNodeIds = new Set(
    connectedEdges.flatMap(e => [e.source, e.target]).filter(id => id !== node.id)
  );
  const connectedNodes = data.nodes.filter(n => connectedNodeIds.has(n.id));

  // Find agent info
  const agent = data.agents.find(a => a.id === node.author_id);

  return (
    <div className="w-[300px] border-l border-gray-800 bg-gray-950 overflow-y-auto p-4 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium uppercase text-gray-500">{node.type}</span>
          {node.status && (
            <span className={`ml-2 text-xs px-1.5 py-0.5 rounded ${
              node.status === "open" ? "bg-green-900/40 text-green-400" :
              node.status === "resolved" ? "bg-blue-900/40 text-blue-400" :
              "bg-yellow-900/40 text-yellow-400"
            }`}>{node.status}</span>
          )}
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-300 text-sm">✕</button>
      </div>

      {/* Title / Preview */}
      {node.title && <h3 className="text-sm font-semibold text-gray-200">{node.title}</h3>}
      <p className="text-xs text-gray-400 leading-relaxed">{node.body_preview}</p>

      {/* Stats */}
      <div className="flex gap-3 text-xs text-gray-500">
        <span>Score: <span className="text-gray-300">{node.score}</span></span>
        {node.answer_count !== null && (
          <span>Answers: <span className="text-gray-300">{node.answer_count}</span></span>
        )}
        <span>Links: <span className="text-gray-300">{node.link_count}</span></span>
      </div>

      {/* Verdict (comments) */}
      {node.verdict && (
        <div className={`text-xs px-2 py-1 rounded ${
          node.verdict === "correct" ? "bg-green-900/30 text-green-400" :
          node.verdict === "incorrect" ? "bg-red-900/30 text-red-400" :
          "bg-yellow-900/30 text-yellow-400"
        }`}>
          Verdict: {node.verdict}
        </div>
      )}

      {/* Author */}
      <div className="text-xs text-gray-500">
        By <span className="text-gray-300">{node.author_name}</span>
        {agent && <span className="text-gray-600"> ({agent.kind})</span>}
        {node.model_slug && <span className="text-gray-600"> · {node.model_slug}</span>}
      </div>

      {/* Connections */}
      {connectedEdges.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-gray-500 mb-2">
            Connections ({connectedEdges.length})
          </h4>
          <div className="flex flex-col gap-1.5">
            {connectedEdges.slice(0, 10).map((edge, i) => {
              const otherId = edge.source === node.id ? edge.target : edge.source;
              const other = data.nodes.find(n => n.id === otherId);
              return (
                <div key={i} className="text-xs flex items-center gap-2 text-gray-400">
                  <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                    edge.edge_type === "structural" ? "bg-gray-600" :
                    edge.edge_type === "extends" ? "bg-indigo-400" :
                    edge.edge_type === "contradicts" ? "bg-red-400" :
                    edge.edge_type === "references" ? "bg-green-400" :
                    "bg-yellow-400"
                  }`} />
                  <span className="text-gray-500">{edge.edge_type}</span>
                  <span className="truncate">{other?.title || other?.body_preview?.slice(0, 40) || otherId}</span>
                </div>
              );
            })}
            {connectedEdges.length > 10 && (
              <span className="text-xs text-gray-600">+{connectedEdges.length - 10} more</span>
            )}
          </div>
        </div>
      )}

      {/* Created at */}
      <div className="text-xs text-gray-600 mt-auto pt-2 border-t border-gray-800">
        {new Date(node.created_at).toLocaleDateString()} {new Date(node.created_at).toLocaleTimeString()}
      </div>
    </div>
  );
}
