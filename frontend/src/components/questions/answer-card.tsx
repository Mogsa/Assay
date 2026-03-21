"use client";

import type { AnswerInQuestion } from "@/lib/types";
import { CommentList } from "./comment-list";
import { CommentForm } from "./comment-form";
import { TimeAgo } from "@/components/ui/time-ago";
import { useAuth } from "@/lib/auth-context";
import { AuthorChip } from "@/components/author-chip";
import { RelatedLinkCard } from "@/components/related-link-card";
import { RatingBlocks } from "@/components/ratings/rating-blocks";

interface AnswerCardProps {
  answer: AnswerInQuestion;
  onRefresh?: () => void;
}

export function AnswerCard({ answer, onRefresh }: AnswerCardProps) {
  const { user } = useAuth();

  return (
    <div
      id={`answer-${answer.id}`}
      className="rounded-2xl border border-xborder bg-xbg-secondary/70 p-4 shadow-[0_20px_50px_-35px_rgba(0,0,0,0.65)]"
    >
      <AuthorChip author={answer.author} />
      <div className="mt-2 whitespace-pre-wrap text-sm">{answer.body}</div>
      <div className="mt-2 text-xs text-xtext-secondary">
        <TimeAgo date={answer.created_at} />
      </div>
      {answer.related.length > 0 && (
        <div className="mt-3 space-y-2">
          {answer.related.map((link) => (
            <RelatedLinkCard key={link.id} link={link} />
          ))}
        </div>
      )}
      <div className="border-t border-gray-800 pt-2 mt-2">
        <RatingBlocks
          targetType="answer"
          targetId={answer.id}
          variant="inline"
          initialFrontierScore={answer.frontier_score}
        />
      </div>
      {answer.comments.length > 0 && (
        <p className="mt-4 text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
          Reviews
        </p>
      )}
      <CommentList comments={answer.comments} />
      {user && onRefresh && (
        <CommentForm
          targetType="answer"
          targetId={answer.id}
          onSubmitted={onRefresh}
          ctaLabel="Review this solution"
          submitLabel="Post review"
          placeholder="Assess this solution, cite flaws, or back it up..."
        />
      )}
    </div>
  );
}
