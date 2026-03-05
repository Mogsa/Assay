"use client";

import type { CommentInQuestion } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";
import { useState } from "react";

const VERDICT_STYLES: Record<string, string> = {
  correct: "bg-xsuccess/20 text-xsuccess",
  incorrect: "bg-xdanger/20 text-xdanger",
  partially_correct: "bg-yellow-500/20 text-yellow-400",
  unsure: "bg-xbg-hover text-xtext-secondary",
};

interface CommentListProps {
  comments: CommentInQuestion[];
  onVoteComment?: (commentId: string, value: 1 | -1) => Promise<void>;
}

export function CommentList({ comments, onVoteComment }: CommentListProps) {
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
          <CommentItem comment={c} onVoteComment={onVoteComment} />
          {replyMap.get(c.id)?.map((r) => (
            <div key={r.id} className="ml-6">
              <CommentItem comment={r} onVoteComment={onVoteComment} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function CommentItem({
  comment,
  onVoteComment,
}: {
  comment: CommentInQuestion;
  onVoteComment?: (commentId: string, value: 1 | -1) => Promise<void>;
}) {
  const [voting, setVoting] = useState(false);

  const handleVote = async (value: 1 | -1) => {
    if (!onVoteComment || voting) return;
    setVoting(true);
    try {
      await onVoteComment(comment.id, value);
    } finally {
      setVoting(false);
    }
  };

  return (
    <div className="flex items-start gap-2 text-sm text-xtext-secondary">
      <div className="flex shrink-0 items-center gap-1 text-xs">
        {onVoteComment && (
          <>
            <button
              onClick={() => handleVote(1)}
              disabled={voting}
              className={comment.viewer_vote === 1 ? "text-xsuccess" : "text-xtext-secondary hover:text-xsuccess"}
              aria-label="Upvote comment"
            >
              ▲
            </button>
            <button
              onClick={() => handleVote(-1)}
              disabled={voting}
              className={comment.viewer_vote === -1 ? "text-xdanger" : "text-xtext-secondary hover:text-xdanger"}
              aria-label="Downvote comment"
            >
              ▼
            </button>
          </>
        )}
        <span className="text-xtext-secondary">{comment.score}</span>
      </div>
      <div className="min-w-0 flex-1">
        <span>{comment.body}</span>
        {comment.verdict && (
          <span
            className={`ml-2 inline-block rounded px-1.5 py-0.5 text-xs font-medium ${VERDICT_STYLES[comment.verdict]}`}
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
