"use client";

import type { AnswerInQuestion } from "@/lib/types";
import { VoteButtons } from "./vote-buttons";
import { CommentList } from "./comment-list";
import { CommentForm } from "./comment-form";
import { TimeAgo } from "@/components/ui/time-ago";
import { votes } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { AuthorChip } from "@/components/author-chip";
import { RelatedLinkCard } from "@/components/related-link-card";

interface AnswerCardProps {
  answer: AnswerInQuestion;
  onRefresh?: () => void;
  onVoteAnswer?: (answerId: string, value: 1 | -1) => Promise<void>;
  onVoteComment?: (commentId: string, value: 1 | -1) => Promise<void>;
}

export function AnswerCard({ answer, onRefresh, onVoteAnswer, onVoteComment }: AnswerCardProps) {
  const { user } = useAuth();

  return (
    <div
      id={`answer-${answer.id}`}
      className="rounded-2xl border border-xborder bg-xbg-secondary/70 p-4 shadow-[0_20px_50px_-35px_rgba(0,0,0,0.65)]"
    >
      <div className="flex gap-4">
        <VoteButtons
          score={answer.score}
          viewerVote={answer.viewer_vote}
          onVote={(value) =>
            onVoteAnswer ? onVoteAnswer(answer.id, value) : votes.answer(answer.id, value).then(() => {})
          }
        />
        <div className="min-w-0 flex-1">
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
          {answer.comments.length > 0 && (
            <p className="mt-4 text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
              Reviews
            </p>
          )}
          <CommentList comments={answer.comments} onVoteComment={onVoteComment} />
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
      </div>
    </div>
  );
}
