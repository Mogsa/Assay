import type { AnswerInQuestion } from "@/lib/types";
import { VoteButtons } from "./vote-buttons";
import { CommentList } from "./comment-list";
import { TimeAgo } from "@/components/ui/time-ago";
import { votes } from "@/lib/api";

export function AnswerCard({ answer }: { answer: AnswerInQuestion }) {
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
      </div>
    </div>
  );
}
