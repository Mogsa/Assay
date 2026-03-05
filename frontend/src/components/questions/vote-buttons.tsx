"use client";

import { useEffect, useState } from "react";

interface VoteButtonsProps {
  score: number;
  onUpvote: () => Promise<void>;
  onDownvote: () => Promise<void>;
}

export function VoteButtons({ score, onUpvote, onDownvote }: VoteButtonsProps) {
  const [currentScore, setCurrentScore] = useState(score);
  const [voting, setVoting] = useState(false);

  useEffect(() => {
    setCurrentScore(score);
  }, [score]);

  const handleVote = async (fn: () => Promise<void>, delta: number) => {
    if (voting) return;
    setVoting(true);
    try {
      await fn();
      setCurrentScore((s) => s + delta);
    } catch {
      // Vote failed
    } finally {
      setVoting(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={() => handleVote(onUpvote, 1)}
        disabled={voting}
        className="text-gray-400 hover:text-green-600"
        aria-label="Upvote"
      >
        ▲
      </button>
      <span className="text-lg font-semibold">{currentScore}</span>
      <button
        onClick={() => handleVote(onDownvote, -1)}
        disabled={voting}
        className="text-gray-400 hover:text-red-600"
        aria-label="Downvote"
      >
        ▼
      </button>
    </div>
  );
}
