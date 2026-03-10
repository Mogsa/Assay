"use client";

import Link from "next/link";
import type { QuestionFeedPreview, QuestionSummary } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { TimeAgo } from "@/components/ui/time-ago";
import { AuthorChip } from "@/components/author-chip";
import { QuestionStatusBadge } from "@/components/question-status-badge";
import { ExecutionModeBadge } from "@/components/execution-mode-badge";
import { FeedPreview } from "./feed-preview";

function excerpt(text: string, limit: number) {
  if (text.length <= limit) return text;
  return `${text.slice(0, limit - 3).trimEnd()}...`;
}

interface FeedCardProps {
  summary: QuestionSummary;
  isExpanded: boolean;
  preview?: QuestionFeedPreview;
  previewLoading?: boolean;
  previewError?: string | null;
  onVote: (questionId: string, value: 1 | -1) => Promise<void>;
  onTogglePreview: (questionId: string) => void;
}

export function FeedCard({
  summary,
  isExpanded,
  preview,
  previewLoading = false,
  previewError = null,
  onVote,
  onTogglePreview,
}: FeedCardProps) {
  return (
    <div className="border-b border-xborder px-4 py-5">
      <div className="flex gap-4">
        <VoteButtons
          score={summary.score}
          viewerVote={summary.viewer_vote}
          onVote={(value) => onVote(summary.id, value)}
        />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-4">
            <button
              type="button"
              onClick={() => onTogglePreview(summary.id)}
              className="block min-w-0 flex-1 text-left focus:outline-none"
            >
              <div className="flex items-start gap-3">
                <span className="mt-1 text-sm text-xtext-secondary">
                  {isExpanded ? "\u25BE" : "\u25B8"}
                </span>
                <div className="min-w-0 flex-1">
                  <h2 className="text-lg font-semibold text-xtext-primary">{summary.title}</h2>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <AuthorChip author={summary.author} compact />
                    <ExecutionModeBadge mode={summary.created_via} compact />
                  </div>
                  <p className="mt-3 text-sm text-xtext-secondary">
                    {excerpt(summary.body, 220)}
                  </p>
                  <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-xtext-secondary">
                    <QuestionStatusBadge status={summary.status} />
                    <TimeAgo date={summary.created_at} />
                    <span>{summary.answer_count} answers</span>
                  </div>
                </div>
              </div>
            </button>
            <Link
              href={`/questions/${summary.id}`}
              className="shrink-0 rounded-full border border-xborder px-3 py-1 text-xs font-medium text-xtext-secondary hover:border-xaccent hover:text-xaccent"
            >
              Full thread
            </Link>
          </div>

          {isExpanded && previewLoading && (
            <div className="mt-4 rounded-3xl border border-dashed border-xborder px-4 py-8 text-sm text-xtext-secondary">
              Loading preview...
            </div>
          )}
          {isExpanded && previewError && (
            <div className="mt-4 rounded-3xl border border-xdanger/30 bg-xdanger/10 px-4 py-3 text-sm text-xdanger">
              {previewError}
            </div>
          )}
          {isExpanded && preview && <FeedPreview preview={preview} />}
        </div>
      </div>
    </div>
  );
}
