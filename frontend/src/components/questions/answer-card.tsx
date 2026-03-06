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
    <div id={`answer-${answer.id}`} className="flex gap-4 border-b border-xborder py-4">
      <VoteButtons
        score={answer.score}
        viewerVote={answer.viewer_vote}
        onVote={(value) =>
          onVoteAnswer ? onVoteAnswer(answer.id, value) : votes.answer(answer.id, value).then(() => {})
        }
      />
      <div className="min-w-0 flex-1">
        <AuthorChip author={answer.author} />
        <div className="whitespace-pre-wrap text-sm">{answer.body}</div>
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
        <CommentList comments={answer.comments} onVoteComment={onVoteComment} />
        {user && onRefresh && (
          <CommentForm
            targetType="answer"
            targetId={answer.id}
            onSubmitted={onRefresh}
          />
        )}
      </div>
    </div>
  );
}
