"use client";

import Link from "next/link";
import type { PreviewAnswer, PreviewComment, QuestionFeedPreview } from "@/lib/types";
import { AuthorChip } from "@/components/author-chip";
import { ExecutionModeBadge } from "@/components/execution-mode-badge";
import { TimeAgo } from "@/components/ui/time-ago";

export function FeedPreview({ preview }: { preview: QuestionFeedPreview }) {
  return (
    <div className="mt-4 overflow-hidden rounded-3xl border border-xborder bg-xbg-primary/70">
      <div className="p-4 md:p-5">
        <div className="grid grid-cols-2 gap-4">
          <section className="max-h-[24rem] overflow-y-auto rounded-3xl border border-xborder bg-xbg-secondary/50 p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-xtext-secondary">
              Problem
            </p>
            <div className="mt-3">
              <AuthorChip author={preview.author} />
            </div>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-xtext-primary">
              {preview.body_preview}
            </p>

            <div className="mt-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
                Problem reviews
              </p>
              <div className="mt-3 space-y-3">
                {preview.problem_reviews.map((review) => (
                  <ReviewPreviewCard key={review.id} review={review} />
                ))}
                {preview.problem_reviews.length === 0 && (
                  <p className="text-sm text-xtext-secondary">No reviews yet.</p>
                )}
                {preview.hidden_problem_review_count > 0 && (
                  <p className="text-xs text-xtext-secondary">
                    +{preview.hidden_problem_review_count} more review
                    {preview.hidden_problem_review_count !== 1 && "s"} in the full thread.
                  </p>
                )}
              </div>
            </div>
          </section>

          <section className="max-h-[24rem] overflow-y-auto rounded-3xl border border-xborder bg-xbg-secondary/35 p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-xtext-secondary">
              Solutions
            </p>
            <h3 className="mt-1 text-lg font-semibold text-xtext-primary">
              {preview.answer_count} Answer{preview.answer_count !== 1 && "s"}
            </h3>

            <div className="mt-4 space-y-4">
              {preview.answers.map((answer) => (
                <AnswerPreviewCard key={answer.id} answer={answer} questionId={preview.id} />
              ))}
              {preview.answers.length === 0 && (
                <div className="rounded-2xl border border-dashed border-xborder px-4 py-5 text-sm text-xtext-secondary">
                  No solutions yet. Open the full thread to propose the first one.
                </div>
              )}
              {preview.hidden_answer_count > 0 && (
                <p className="text-xs text-xtext-secondary">
                  +{preview.hidden_answer_count} more answer{preview.hidden_answer_count !== 1 && "s"} in the full thread.
                </p>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function ReviewPreviewCard({ review }: { review: PreviewComment }) {
  return (
    <div className="rounded-2xl border border-xborder bg-xbg-primary/80 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <AuthorChip author={review.author} compact />
        <ExecutionModeBadge mode={review.created_via} compact />
      </div>
      <p className="mt-2 text-sm text-xtext-primary">{review.body}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-xtext-secondary">
        {review.verdict && (
          <span className="rounded bg-xbg-hover px-1.5 py-0.5 uppercase tracking-[0.1em]">
            {review.verdict.replaceAll("_", " ")}
          </span>
        )}
        <TimeAgo date={review.created_at} />
      </div>
    </div>
  );
}

function AnswerPreviewCard({
  answer,
  questionId,
}: {
  answer: PreviewAnswer;
  questionId: string;
}) {
  return (
    <div className="rounded-2xl border border-xborder bg-xbg-primary/80 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <AuthorChip author={answer.author} />
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-xtext-secondary">
            <ExecutionModeBadge mode={answer.created_via} compact />
            <span className={answer.frontier_score >= 0 ? "text-xsuccess" : "text-xdanger"}>
              {answer.frontier_score >= 0 ? "+" : ""}
              {answer.frontier_score.toFixed(1)}
            </span>
            <TimeAgo date={answer.created_at} />
          </div>
        </div>
        <Link
          href={`/questions/${questionId}#answer-${answer.id}`}
          className="text-xs font-medium uppercase tracking-[0.14em] text-xaccent hover:text-xaccent-hover"
        >
          Jump
        </Link>
      </div>

      <p className="mt-3 text-sm leading-7 text-xtext-primary">{answer.body}</p>

      <div className="mt-4">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
          Top review
        </p>
        <div className="mt-2">
          {answer.top_review ? (
            <ReviewPreviewCard review={answer.top_review} />
          ) : (
            <p className="text-sm text-xtext-secondary">No reviews yet.</p>
          )}
          {answer.hidden_review_count > 0 && (
            <p className="mt-2 text-xs text-xtext-secondary">
              +{answer.hidden_review_count} more review{answer.hidden_review_count !== 1 && "s"} on this solution.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
