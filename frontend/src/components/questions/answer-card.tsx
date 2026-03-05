import type { AnswerInQuestion } from "@/lib/types";
import { VoteButtons } from "./vote-buttons";
import { CommentList } from "./comment-list";
import { CommentForm } from "./comment-form";
import { TimeAgo } from "@/components/ui/time-ago";
import { votes } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface AnswerCardProps {
  answer: AnswerInQuestion;
  onRefresh?: () => void;
}

export function AnswerCard({ answer, onRefresh }: AnswerCardProps) {
  const { user } = useAuth();

  return (
    <div className="flex gap-4 border-b border-gray-100 py-4">
      <VoteButtons
        score={answer.score}
        onUpvote={() => votes.answer(answer.id, 1)}
        onDownvote={() => votes.answer(answer.id, -1)}
      />
      <div className="min-w-0 flex-1">
        <div className="whitespace-pre-wrap text-sm">{answer.body}</div>
        <div className="mt-2 text-xs text-gray-400">
          <TimeAgo date={answer.created_at} />
        </div>
        <CommentList comments={answer.comments} />
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
