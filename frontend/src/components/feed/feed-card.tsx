"use client";

import Link from "next/link";
import type { QuestionFeedPreview, QuestionSummary } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { TimeAgo } from "@/components/ui/time-ago";
import { AuthorChip } from "@/components/author-chip";
import { QuestionStatusBadge } from "@/components/question-status-badge";
import { FeedPreview } from "./feed-preview";
import { ExecutionModeBadge } from "@/components/execution-mode-badge";

function excerpt(text: string, limit: number) {
  if (text.length <= limit) return text;
  return `${text.slice(0, limit - 3).trimEnd()}...`;
}

interface FeedCardProps {
  summary: QuestionSummary;
  score: number;
  viewerVote: QuestionSummary["viewer_vote"];
  isExpanded: boolean;
  preview?: QuestionFeedPreview;
  previewLoading?: boolean;
  previewError?: string | null;
  onVote: (questionId: string, value: 1 | -1) => Promise<void>;
  onTogglePreview: (questionId: string) => void;
}

export function FeedCard({
  summary,
  score,
  viewerVote,
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
        <VoteButtons score={score} viewerVote={viewerVote} onVote={handleQuestionVote} />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-4">
            <button
              type="button"
              onClick={() => onTogglePreview(summary.id)}
              className="block min-w-0 flex-1 rounded-2xl text-left transition-colors hover:bg-xbg-hover/50 focus:outline-none"
            >
              <div className="flex items-start gap-3">
                <span className="mt-1 text-sm text-xtext-secondary">
                  {isExpanded ? "▾" : "▸"}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-3">
                    <h2 className="text-lg font-semibold text-xtext-primary">{summary.title}</h2>
                    <ExecutionModeBadge mode={summary.created_via} compact />
                  </div>
                  <div className="mt-2">
                    <AuthorChip author={summary.author} />
                  </div>
                  <p className="mt-3 whitespace-pre-wrap text-sm text-xtext-secondary">
                    {excerpt(summary.body, 180)}
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
              className="shrink-0 rounded-full border border-xaccent px-3 py-1 text-xs font-medium uppercase tracking-[0.14em] text-xaccent hover:bg-xaccent/10"
            >
              Open
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

  async function handleQuestionVote(value: 1 | -1) {
    await onVote(summary.id, value);
  }
}
