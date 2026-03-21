"use client";

import type { CommentInQuestion } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";
import { AuthorChip } from "@/components/author-chip";

const VERDICT_STYLES: Record<string, string> = {
  correct: "bg-xsuccess/20 text-xsuccess",
  incorrect: "bg-xdanger/20 text-xdanger",
  partially_correct: "bg-yellow-500/20 text-yellow-400",
  unsure: "bg-xbg-hover text-xtext-secondary",
};

interface CommentListProps {
  comments: CommentInQuestion[];
}

export function CommentList({ comments }: CommentListProps) {
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
    <div className="mt-3 border-t border-xborder pt-3">
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
    <div className="flex items-start gap-2 text-sm text-xtext-secondary">
      <div className="min-w-0 flex-1">
        <AuthorChip author={comment.author} compact />
        <p className="mt-1">{comment.body}</p>
        {comment.verdict && (
          <span
            className={`mt-1 inline-block rounded px-1.5 py-0.5 text-xs font-medium ${VERDICT_STYLES[comment.verdict]}`}
          >
            {comment.verdict.replaceAll("_", " ")}
          </span>
        )}
        <span className="ml-2 text-xs text-xtext-secondary">
          <TimeAgo date={comment.created_at} />
        </span>
      </div>
    </div>
  );
}
