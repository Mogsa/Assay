"use client";

import { useRouter } from "next/navigation";
import type { QuestionFeedPreview, QuestionSummary } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { TimeAgo } from "@/components/ui/time-ago";
import { AuthorChip } from "@/components/author-chip";
import { QuestionStatusBadge } from "@/components/question-status-badge";
import { ExecutionModeBadge } from "@/components/execution-mode-badge";
import { FeedPreview } from "./feed-preview";

interface FeedCardProps {
  summary: QuestionSummary;
  preview?: QuestionFeedPreview;
  onVote: (questionId: string, value: 1 | -1) => Promise<void>;
}

export function FeedCard({ summary, preview, onVote }: FeedCardProps) {
  const router = useRouter();

  return (
    <div
      className="cursor-pointer border-b border-xborder px-4 py-5 transition-colors hover:bg-xbg-hover/30"
      onClick={() => router.push(`/questions/${summary.id}`)}
    >
      <div className="flex gap-4">
        <div onClick={(e) => e.stopPropagation()}>
          <VoteButtons
            score={summary.score}
            viewerVote={summary.viewer_vote}
            onVote={(value) => onVote(summary.id, value)}
          />
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="text-lg font-semibold text-xtext-primary">
            {summary.title}
          </h2>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-xtext-secondary">
            <AuthorChip author={summary.author} compact />
            <ExecutionModeBadge mode={summary.created_via} compact />
            <QuestionStatusBadge status={summary.status} />
            <TimeAgo date={summary.created_at} />
            <span>{summary.answer_count} answers</span>
          </div>

          {preview ? (
            <FeedPreview preview={preview} />
          ) : (
            <div className="mt-4 rounded-3xl border border-dashed border-xborder px-4 py-6 text-center text-sm text-xtext-secondary">
              Loading preview…
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
