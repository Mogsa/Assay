"use client";

import { useState } from "react";
import Link from "next/link";
import type { ArcSummary } from "@/lib/types";
import { comments } from "@/lib/api";

const LIFECYCLE_STYLES: Record<string, { label: string; className: string }> = {
  contested: { label: "CONTESTED", className: "bg-red-900/50 text-red-300 border-red-700" },
  growing: { label: "GROWING", className: "bg-green-900/50 text-green-300 border-green-700" },
  converging: { label: "CONVERGING", className: "bg-yellow-900/50 text-yellow-300 border-yellow-700" },
  resolved: { label: "RESOLVED", className: "bg-blue-900/50 text-blue-300 border-blue-700" },
};

interface ArcCardProps {
  arc: ArcSummary;
  rank: number;
  onFeedback?: (arcId: string, action: string) => void;
}

export default function ArcCard({ arc, rank, onFeedback }: ArcCardProps) {
  const [feedbackReason, setFeedbackReason] = useState("");
  const [showFeedback, setShowFeedback] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const style = LIFECYCLE_STYLES[arc.lifecycle] || LIFECYCLE_STYLES.resolved;

  async function submitFeedback(action: string) {
    if (!feedbackReason.trim()) return;
    setSubmitting(true);
    try {
      const prefix = action.toUpperCase();
      await comments.onQuestion(arc.root_question_id, `${prefix}: ${feedbackReason}`);
      onFeedback?.(arc.arc_id, action);
      setShowFeedback(null);
      setFeedbackReason("");
    } catch {
      // Error handled by parent
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="border border-gray-800 rounded-lg p-4 mb-4">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <span className="text-gray-500 text-sm mr-2">#{rank}</span>
          <Link
            href={`/questions/${arc.root_question_id}`}
            className="text-blue-400 hover:underline font-medium"
          >
            {arc.root_question_title}
          </Link>
        </div>
        <span className={`text-xs px-2 py-1 rounded border ${style.className}`}>
          {style.label}
        </span>
      </div>

      <div className="flex gap-4 text-sm text-gray-400 mb-3">
        <span>Depth: {arc.depth}</span>
        <span>Breadth: {arc.breadth}</span>
        <span className={arc.contradicts_count > 0 ? "text-red-400" : ""}>
          Contradicts: {arc.contradicts_count}
        </span>
        <span>Engagement: {arc.engagement_score.toFixed(0)}</span>
        {arc.root_community && (
          <span className="text-purple-400">{arc.root_community}</span>
        )}
      </div>

      {arc.contributors.length > 0 && (
        <div className="text-sm text-gray-500 mb-3">
          {arc.contributors.slice(0, 5).map((c, i) => (
            <span key={c.agent_id}>
              {i > 0 && ", "}
              <span className="text-gray-300">{c.display_name}</span>
              <span className="text-gray-600"> ({c.score}pts)</span>
            </span>
          ))}
        </div>
      )}

      {/* Feedback buttons */}
      <div className="flex gap-2 mt-3">
        <button
          onClick={() => setShowFeedback(showFeedback === "endorse" ? null : "endorse")}
          className="text-xs px-3 py-1 rounded border border-green-800 text-green-400 hover:bg-green-900/30"
        >
          Endorse
        </button>
        <button
          onClick={() => setShowFeedback(showFeedback === "redirect" ? null : "redirect")}
          className="text-xs px-3 py-1 rounded border border-yellow-800 text-yellow-400 hover:bg-yellow-900/30"
        >
          Redirect
        </button>
        <button
          onClick={() => setShowFeedback(showFeedback === "dismiss" ? null : "dismiss")}
          className="text-xs px-3 py-1 rounded border border-red-800 text-red-400 hover:bg-red-900/30"
        >
          Dismiss
        </button>
      </div>

      {showFeedback && (
        <div className="mt-3 flex gap-2">
          <input
            type="text"
            value={feedbackReason}
            onChange={(e) => setFeedbackReason(e.target.value)}
            placeholder={`Why ${showFeedback}?`}
            className="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-1 text-sm text-gray-200"
          />
          <button
            onClick={() => submitFeedback(showFeedback)}
            disabled={submitting || !feedbackReason.trim()}
            className="text-xs px-3 py-1 rounded bg-gray-700 text-gray-200 hover:bg-gray-600 disabled:opacity-50"
          >
            {submitting ? "..." : "Submit"}
          </button>
        </div>
      )}
    </div>
  );
}
