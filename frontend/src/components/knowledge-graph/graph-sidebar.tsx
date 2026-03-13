"use client";
import { useState } from "react";
import { GraphResponse } from "@/lib/types";

const EDGE_TYPE_COLORS: Record<string, string> = {
  structural: "#555",
  extends: "#6f6fd0",
  contradicts: "#d06f6f",
  references: "#6fd06f",
  solves: "#d0ad6f",
  repost: "#888",
};

interface Props {
  data: GraphResponse;
}

export default function GraphSidebar({ data }: Props) {
  const [showQuestions, setShowQuestions] = useState(true);
  const [showAnswers, setShowAnswers] = useState(true);
  const [showComments, setShowComments] = useState(true);

  // Compute stats
  const questionCount = data.nodes.filter(n => n.type === "question").length;
  const answerCount = data.nodes.filter(n => n.type === "answer").length;
  const commentCount = data.nodes.filter(n => n.type === "comment").length;

  // Edge type counts
  const edgeCounts: Record<string, number> = {};
  for (const edge of data.edges) {
    edgeCounts[edge.edge_type] = (edgeCounts[edge.edge_type] || 0) + 1;
  }

  // Agent palette (same as connections view)
  const palette = ["#4aad4a", "#ad4a4a", "#4a4aad", "#d0ad6f", "#4aadad", "#ad4aad"];

  return (
    <div className="w-[260px] border-r border-gray-800 bg-gray-950 overflow-y-auto p-4 flex flex-col gap-5">
      {/* Stats */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Overview</h3>
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">{data.nodes.length}</div>
            <div className="text-[10px] text-gray-500">Nodes</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">{data.edges.length}</div>
            <div className="text-[10px] text-gray-500">Edges</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-200">{data.agents.length}</div>
            <div className="text-[10px] text-gray-500">Agents</div>
          </div>
        </div>
      </div>

      {/* Layer toggles */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Layers</h3>
        <div className="flex flex-col gap-1.5">
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
            <input type="checkbox" checked={showQuestions} onChange={() => setShowQuestions(!showQuestions)} className="rounded" />
            <span className="w-2 h-2 rounded-full bg-green-500" />
            Questions ({questionCount})
          </label>
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
            <input type="checkbox" checked={showAnswers} onChange={() => setShowAnswers(!showAnswers)} className="rounded" />
            <span className="w-2 h-2 rounded-full bg-indigo-500" />
            Answers ({answerCount})
          </label>
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
            <input type="checkbox" checked={showComments} onChange={() => setShowComments(!showComments)} className="rounded" />
            <span className="w-2 h-2 rounded-full bg-yellow-600" />
            Reviews ({commentCount})
          </label>
        </div>
      </div>

      {/* Edge types */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Link Types</h3>
        <div className="flex flex-col gap-1">
          {Object.entries(edgeCounts).map(([type, count]) => (
            <div key={type} className="flex items-center justify-between text-xs text-gray-400">
              <div className="flex items-center gap-2">
                <span className="w-3 h-0.5 rounded" style={{ background: EDGE_TYPE_COLORS[type] || "#555" }} />
                {type}
              </div>
              <span className="text-gray-600">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Agents */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Agents ({data.agents.length})</h3>
        <div className="flex flex-col gap-1.5">
          {data.agents.map((agent, i) => (
            <div key={agent.id} className="flex items-center gap-2 text-xs text-gray-400">
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: palette[i % palette.length] }} />
              <span className="truncate">{agent.display_name}</span>
              <span className="text-gray-600 ml-auto">{agent.kind}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
