"use client";

import { useEffect } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import type { PreviewAnswer, PreviewComment, QuestionFeedPreview } from "@/lib/types";
import { AuthorChip } from "@/components/author-chip";
import { ExecutionModeBadge } from "@/components/execution-mode-badge";
import { QuestionStatusBadge } from "@/components/question-status-badge";
import { TimeAgo } from "@/components/ui/time-ago";

interface QuestionOverlayProps {
  preview: QuestionFeedPreview;
  onClose: () => void;
}

export function QuestionOverlay({ preview, onClose }: QuestionOverlayProps) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/80 backdrop-blur-sm"
      style={{ animation: "overlay-fade-in 150ms ease-out" }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative mx-4 mt-8 mb-8 flex max-h-[calc(100vh-4rem)] w-full max-w-[1200px] flex-col rounded-3xl border border-xborder bg-xbg-primary shadow-2xl" style={{ animation: "overlay-slide-up 200ms ease-out" }}>
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-xborder px-6 py-4">
          <div className="min-w-0 flex-1">
            <h2 className="text-xl font-bold text-xtext-primary">{preview.title}</h2>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-xtext-secondary">
              <AuthorChip author={preview.author} compact />
              <QuestionStatusBadge status={preview.status} />
              <ExecutionModeBadge mode={preview.created_via} compact />
              <TimeAgo date={preview.created_at} />
              <span>{preview.answer_count} answers</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href={`/questions/${preview.id}`}
              className="rounded-full border border-xaccent px-4 py-1.5 text-xs font-medium uppercase tracking-[0.14em] text-xaccent hover:bg-xaccent/10"
            >
              Full thread
            </Link>
            <button
              onClick={onClose}
              className="flex h-8 w-8 items-center justify-center rounded-full text-xtext-secondary transition-colors hover:bg-xbg-hover hover:text-xtext-primary"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Two-column body */}
        <div className="grid min-h-0 flex-1 grid-cols-2 divide-x divide-xborder">
          {/* Problem column */}
          <div className="overflow-y-auto p-6">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-xtext-secondary">
              Problem
            </p>
            <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-xtext-primary">
              {preview.body_preview}
            </p>

            {preview.problem_reviews.length > 0 && (
              <div className="mt-6">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
                  Reviews ({preview.problem_reviews.length}
                  {preview.hidden_problem_review_count > 0 ? `+${preview.hidden_problem_review_count}` : ""})
                </p>
                <div className="mt-3 space-y-3">
                  {preview.problem_reviews.map((review) => (
                    <ReviewCard key={review.id} review={review} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Solutions column */}
          <div className="overflow-y-auto p-6">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-xtext-secondary">
              Solutions
            </p>
            <p className="mt-1 text-lg font-semibold text-xtext-primary">
              {preview.answer_count} Answer{preview.answer_count !== 1 && "s"}
            </p>

            <div className="mt-4 space-y-4">
              {preview.answers.map((answer) => (
                <AnswerCard key={answer.id} answer={answer} questionId={preview.id} />
              ))}
              {preview.answers.length === 0 && (
                <p className="text-sm text-xtext-secondary">No solutions yet.</p>
              )}
              {preview.hidden_answer_count > 0 && (
                <p className="text-xs text-xtext-secondary">
                  +{preview.hidden_answer_count} more in full thread.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}

function ReviewCard({ review }: { review: PreviewComment }) {
  return (
    <div className="rounded-2xl border border-xborder bg-xbg-secondary/50 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <AuthorChip author={review.author} compact />
        {review.verdict && (
          <span className="rounded bg-xbg-hover px-1.5 py-0.5 text-[10px] uppercase tracking-[0.1em] text-xtext-secondary">
            {review.verdict.replaceAll("_", " ")}
          </span>
        )}
        <span className={review.score >= 0 ? "text-xs text-xsuccess" : "text-xs text-xdanger"}>
          {review.score >= 0 ? "+" : ""}{review.score}
        </span>
      </div>
      <p className="mt-2 text-sm leading-6 text-xtext-primary">{review.body}</p>
    </div>
  );
}

function AnswerCard({ answer, questionId }: { answer: PreviewAnswer; questionId: string }) {
  return (
    <div className="rounded-2xl border border-xborder bg-xbg-secondary/50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <AuthorChip author={answer.author} />
          <span className={answer.score >= 0 ? "text-xs text-xsuccess" : "text-xs text-xdanger"}>
            {answer.score >= 0 ? "+" : ""}{answer.score}
          </span>
        </div>
        <Link
          href={`/questions/${questionId}#answer-${answer.id}`}
          className="text-xs font-medium text-xaccent hover:text-xaccent-hover"
        >
          Full thread →
        </Link>
      </div>
      <p className="mt-3 text-sm leading-7 text-xtext-primary">{answer.body}</p>
      {answer.top_review && (
        <div className="mt-3 border-t border-xborder pt-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
            Top review
          </p>
          <div className="mt-2">
            <ReviewCard review={answer.top_review} />
          </div>
          {answer.hidden_review_count > 0 && (
            <p className="mt-2 text-xs text-xtext-secondary">
              +{answer.hidden_review_count} more reviews
            </p>
          )}
        </div>
      )}
    </div>
  );
}
