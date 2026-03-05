import type { CommentInQuestion } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";

const VERDICT_STYLES: Record<string, string> = {
  correct: "bg-green-100 text-green-800",
  incorrect: "bg-red-100 text-red-800",
  partially_correct: "bg-yellow-100 text-yellow-800",
  unsure: "bg-gray-100 text-gray-600",
};

export function CommentList({ comments }: { comments: CommentInQuestion[] }) {
  const topLevel = comments.filter((c) => !c.parent_id);
  const replies = comments.filter((c) => c.parent_id);
  const replyMap = new Map<string, CommentInQuestion[]>();
  for (const r of replies) {
    const existing = replyMap.get(r.parent_id!) || [];
    existing.push(r);
    replyMap.set(r.parent_id!, existing);
  }

  if (topLevel.length === 0) return null;

  return (
    <div className="mt-3 border-t border-gray-100 pt-3">
      {topLevel.map((c) => (
        <div key={c.id} className="py-1">
          <CommentItem comment={c} />
          {replyMap.get(c.id)?.map((r) => (
            <div key={r.id} className="ml-6">
              <CommentItem comment={r} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function CommentItem({ comment }: { comment: CommentInQuestion }) {
  return (
    <div className="flex items-start gap-2 text-sm text-gray-600">
      <span className="shrink-0 text-xs text-gray-400">{comment.score}</span>
      <div className="min-w-0 flex-1">
        <span>{comment.body}</span>
        {comment.verdict && (
          <span
            className={`ml-2 inline-block rounded px-1.5 py-0.5 text-xs font-medium ${VERDICT_STYLES[comment.verdict]}`}
          >
            {comment.verdict.replace("_", " ")}
          </span>
        )}
        <span className="ml-2 text-xs text-gray-400">
          <TimeAgo date={comment.created_at} />
        </span>
      </div>
    </div>
  );
}
