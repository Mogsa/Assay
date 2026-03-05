"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { questions as questionsApi, votes } from "@/lib/api";
import type { QuestionDetail, QuestionSummary, CommentInQuestion } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { TimeAgo } from "@/components/ui/time-ago";

export function FeedCard({ summary }: { summary: QuestionSummary }) {
  const [detail, setDetail] = useState<QuestionDetail | null>(null);

  useEffect(() => {
    questionsApi.get(summary.id).then(setDetail).catch(() => {});
  }, [summary.id]);

  const sortedAnswers = detail
    ? [...detail.answers].sort((a, b) => b.score - a.score)
    : [];

  const sortedComments = detail
    ? [...detail.comments].sort((a, b) => b.score - a.score)
    : [];

  const handleQuestionVote = async (value: 1 | -1) => {
    const result = await votes.question(summary.id, value);
    setDetail((prev) =>
      prev ? { ...prev, viewer_vote: result.viewer_vote, upvotes: result.upvotes, downvotes: result.downvotes, score: result.score } : prev
    );
  };

  const handleAnswerVote = async (answerId: string, value: 1 | -1) => {
    const result = await votes.answer(answerId, value);
    setDetail((prev) =>
      prev
        ? {
            ...prev,
            answers: prev.answers.map((a) =>
              a.id === answerId
                ? { ...a, viewer_vote: result.viewer_vote, upvotes: result.upvotes, downvotes: result.downvotes, score: result.score }
                : a
            ),
          }
        : prev
    );
  };

  return (
    <div className="border-b border-xborder">
      {/* Question title bar */}
      <div className="border-b border-xborder px-4 py-3">
        <Link href={`/questions/${summary.id}`} className="text-base font-bold text-xtext-primary hover:underline">
          {summary.title}
        </Link>
        <div className="mt-1 flex items-center gap-3 text-xs text-xtext-secondary">
          <span className="capitalize">{summary.status}</span>
          <TimeAgo date={summary.created_at} />
          <span>{summary.answer_count} answers</span>
        </div>
      </div>

      {/* Dual pane */}
      <div className="flex">
        {/* Left: Question thread */}
        <div className="flex-1 border-r border-xborder">
          <div className="max-h-[400px] overflow-y-auto p-4">
            <div className="flex gap-3">
              <VoteButtons score={detail?.score ?? summary.score} viewerVote={detail?.viewer_vote ?? summary.viewer_vote} onVote={handleQuestionVote} />
              <div className="min-w-0 flex-1">
                <p className="whitespace-pre-wrap text-sm text-xtext-primary">{summary.body}</p>
              </div>
            </div>

            {/* Question comments */}
            {sortedComments.length > 0 && (
              <div className="mt-3 border-t border-xborder pt-3">
                <p className="mb-2 text-xs font-medium text-xtext-secondary">{sortedComments.length} comments</p>
                {sortedComments.map((c) => (
                  <MiniComment key={c.id} comment={c} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Answer list */}
        <div className="flex-1">
          <div className="max-h-[400px] overflow-y-auto p-4">
            {sortedAnswers.length === 0 ? (
              <p className="py-4 text-center text-sm text-xtext-secondary">No answers yet</p>
            ) : (
              <div className="space-y-4">
                {sortedAnswers.map((a) => (
                  <div key={a.id} className="border-b border-xborder pb-3 last:border-0">
                    <div className="flex gap-3">
                      <VoteButtons score={a.score} viewerVote={a.viewer_vote} onVote={(v) => handleAnswerVote(a.id, v)} />
                      <div className="min-w-0 flex-1">
                        <p className="whitespace-pre-wrap text-sm text-xtext-primary">{a.body}</p>
                        <p className="mt-1 text-xs text-xtext-secondary"><TimeAgo date={a.created_at} /></p>
                      </div>
                    </div>
                    {/* Answer comments */}
                    {a.comments.length > 0 && (
                      <div className="ml-9 mt-2 border-t border-xborder pt-2">
                        {[...a.comments].sort((x, y) => y.score - x.score).map((c) => (
                          <MiniComment key={c.id} comment={c} />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MiniComment({ comment }: { comment: CommentInQuestion }) {
  return (
    <div className="flex items-start gap-2 py-1 text-xs">
      <span className={`shrink-0 ${comment.score > 0 ? "text-xsuccess" : comment.score < 0 ? "text-xdanger" : "text-xtext-secondary"}`}>
        {comment.score}
      </span>
      <p className="min-w-0 flex-1 text-xtext-primary">{comment.body}</p>
      <span className="shrink-0 text-xtext-secondary"><TimeAgo date={comment.created_at} /></span>
    </div>
  );
}
