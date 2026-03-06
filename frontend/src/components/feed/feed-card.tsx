"use client";

import { useState } from "react";
import Link from "next/link";
import { votes } from "@/lib/api";
import type { QuestionSummary } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { TimeAgo } from "@/components/ui/time-ago";
import { AuthorChip } from "@/components/author-chip";
import { QuestionStatusBadge } from "@/components/question-status-badge";

export function FeedCard({ summary }: { summary: QuestionSummary }) {
  const [score, setScore] = useState(summary.score);
  const [viewerVote, setViewerVote] = useState(summary.viewer_vote);

  const handleQuestionVote = async (value: 1 | -1) => {
    const result = await votes.question(summary.id, value);
    setScore(result.score);
    setViewerVote(result.viewer_vote);
  };

  return (
    <div className="border-b border-xborder px-4 py-5">
      <div className="flex gap-4">
        <VoteButtons score={score} viewerVote={viewerVote} onVote={handleQuestionVote} />
        <div className="min-w-0 flex-1">
          <Link href={`/questions/${summary.id}`} className="text-lg font-semibold text-xtext-primary hover:text-xaccent">
            {summary.title}
          </Link>
          <div className="mt-2">
            <AuthorChip author={summary.author} />
          </div>
          <p className="mt-3 whitespace-pre-wrap text-sm text-xtext-secondary">{summary.body}</p>
          <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-xtext-secondary">
            <QuestionStatusBadge status={summary.status} />
            <TimeAgo date={summary.created_at} />
            <span>{summary.answer_count} answers</span>
          </div>
        </div>
      </div>
    </div>
  );
}
