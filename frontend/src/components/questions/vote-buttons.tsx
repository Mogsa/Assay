"use client";

import { useState } from "react";
import type { ViewerVote } from "@/lib/types";

interface VoteButtonsProps {
  score: number;
  viewerVote: ViewerVote;
  onVote: (value: 1 | -1) => Promise<void>;
}

export function VoteButtons({ score, viewerVote, onVote }: VoteButtonsProps) {
  const [voting, setVoting] = useState(false);
  const [error, setError] = useState(false);

  const handleVote = async (value: 1 | -1) => {
    if (voting) return;
    if (viewerVote === value) return; // Already voted this way — no-op
    setVoting(true);
    setError(false);
    try {
      await onVote(value);
    } catch {
      setError(true);
      setTimeout(() => setError(false), 2000);
    } finally {
      setVoting(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={() => handleVote(1)}
        disabled={voting}
        className={`transition-colors ${voting ? "opacity-40 cursor-not-allowed" : ""} ${
          viewerVote === 1 ? "text-xsuccess" : "text-xtext-secondary hover:text-xsuccess"
        }`}
        aria-label="Upvote"
      >
        ▲
      </button>
      <span className={`text-lg font-semibold ${error ? "text-xdanger" : ""}`}>
        {score}
      </span>
      <button
        onClick={() => handleVote(-1)}
        disabled={voting}
        className={`transition-colors ${voting ? "opacity-40 cursor-not-allowed" : ""} ${
          viewerVote === -1 ? "text-xdanger" : "text-xtext-secondary hover:text-xdanger"
        }`}
        aria-label="Downvote"
      >
        ▼
      </button>
    </div>
  );
}
