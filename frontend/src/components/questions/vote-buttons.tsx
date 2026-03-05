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

  const handleVote = async (value: 1 | -1) => {
    if (voting) return;
    setVoting(true);
    try {
      await onVote(value);
    } catch {
      // Vote failed
    } finally {
      setVoting(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={() => handleVote(1)}
        disabled={voting}
        className={`hover:text-xsuccess ${viewerVote === 1 ? "text-xsuccess" : "text-xtext-secondary"}`}
        aria-label="Upvote"
      >
        ▲
      </button>
      <span className="text-lg font-semibold">{score}</span>
      <button
        onClick={() => handleVote(-1)}
        disabled={voting}
        className={`hover:text-xdanger ${viewerVote === -1 ? "text-xdanger" : "text-xtext-secondary"}`}
        aria-label="Downvote"
      >
        ▼
      </button>
    </div>
  );
}
