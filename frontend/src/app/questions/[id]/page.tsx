"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ApiError, questions as questionsApi, votes } from "@/lib/api";
import type { CommentInQuestion, QuestionDetail, VoteMutationResult } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { CommentList } from "@/components/questions/comment-list";
import { AnswerCard } from "@/components/questions/answer-card";
import { AnswerForm } from "@/components/questions/answer-form";
import { CommentForm } from "@/components/questions/comment-form";
import { TimeAgo } from "@/components/ui/time-ago";
import { useAuth } from "@/lib/auth-context";
import { AuthorChip } from "@/components/author-chip";
import { QuestionStatusBadge } from "@/components/question-status-badge";
import { RelatedLinkCard } from "@/components/related-link-card";

export default function QuestionPage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [question, setQuestion] = useState<QuestionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshQuestion = useCallback(() => {
    questionsApi
      .get(params.id)
      .then(setQuestion)
      .catch((e) => setError(e instanceof ApiError ? e.detail : "Failed to load question"));
  }, [params.id]);

  useEffect(() => {
    refreshQuestion();
  }, [refreshQuestion]);

  if (error) return <p className="py-8 text-center text-xdanger">{error}</p>;
  if (!question) return <p className="py-8 text-center text-xtext-secondary">Loading\u2026</p>;

  const patchCommentVote = (
    comments: CommentInQuestion[],
    commentId: string,
    result: VoteMutationResult,
  ): CommentInQuestion[] =>
    comments.map((comment) =>
      comment.id === commentId
        ? {
            ...comment,
            viewer_vote: result.viewer_vote,
            upvotes: result.upvotes,
            downvotes: result.downvotes,
            score: result.score,
          }
        : comment,
    );

  const handleQuestionVote = async (value: 1 | -1) => {
    const result = await votes.question(question.id, value);
    setQuestion((prev) =>
      prev
        ? {
            ...prev,
            viewer_vote: result.viewer_vote,
            upvotes: result.upvotes,
            downvotes: result.downvotes,
            score: result.score,
          }
        : prev,
    );
  };

  const handleAnswerVote = async (answerId: string, value: 1 | -1) => {
    const result = await votes.answer(answerId, value);
    setQuestion((prev) =>
      prev
        ? {
            ...prev,
            answers: prev.answers.map((answer) =>
              answer.id === answerId
                ? {
                    ...answer,
                    viewer_vote: result.viewer_vote,
                    upvotes: result.upvotes,
                    downvotes: result.downvotes,
                    score: result.score,
                  }
                : answer,
            ),
          }
        : prev,
    );
  };

  const handleCommentVote = async (commentId: string, value: 1 | -1) => {
    const result = await votes.comment(commentId, value);
    setQuestion((prev) =>
      prev
        ? {
            ...prev,
            comments: patchCommentVote(prev.comments, commentId, result),
            answers: prev.answers.map((answer) => ({
              ...answer,
              comments: patchCommentVote(answer.comments, commentId, result),
            })),
          }
        : prev,
    );
  };

  const canUpdateStatus = !!user;

  const handleStatusUpdate = async (status: "open" | "answered" | "resolved") => {
    try {
      const updated = await questionsApi.updateStatus(question.id, status);
      setQuestion((prev) =>
        prev
          ? {
              ...prev,
              status: updated.status,
            }
          : prev,
      );
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Failed to update question");
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight">{question.title}</h1>
      <div className="mt-3">
        <AuthorChip author={question.author} />
      </div>
      <div className="mt-2 flex flex-wrap gap-4 text-sm text-xtext-secondary">
        <QuestionStatusBadge status={question.status} />
        <TimeAgo date={question.created_at} />
        <span>{question.answer_count} answers</span>
      </div>
      {canUpdateStatus && (
        <div className="mt-3 flex flex-wrap gap-2">
          {(["open", "answered", "resolved"] as const).map((status) => (
            <button
              key={status}
              onClick={() => handleStatusUpdate(status)}
              className={`rounded-full border px-3 py-1 text-xs uppercase tracking-[0.12em] ${
                question.status === status
                  ? "border-xaccent bg-xaccent/10 text-xaccent"
                  : "border-xborder text-xtext-secondary hover:bg-xbg-hover"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      )}

      <div className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
        <section className="rounded-3xl border border-xborder bg-xbg-secondary/60 p-5 shadow-[0_30px_80px_-55px_rgba(0,0,0,0.8)]">
          <div className="flex gap-4">
            <VoteButtons
              score={question.score}
              viewerVote={question.viewer_vote}
              onVote={handleQuestionVote}
            />
            <div className="min-w-0 flex-1">
              <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-xtext-secondary">
                Problem
              </p>
              <div className="mt-3 whitespace-pre-wrap text-sm leading-7">{question.body}</div>
              {question.related.length > 0 && (
                <div className="mt-5">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
                    References and reposts
                  </p>
                  <div className="mt-2 space-y-2">
                    {question.related.map((link) => (
                      <RelatedLinkCard key={link.id} link={link} />
                    ))}
                  </div>
                </div>
              )}
              {question.comments.length > 0 && (
                <p className="mt-5 text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
                  Problem reviews
                </p>
              )}
              <CommentList comments={question.comments} onVoteComment={handleCommentVote} />
              {user && (
                <CommentForm
                  targetType="question"
                  targetId={question.id}
                  onSubmitted={refreshQuestion}
                  ctaLabel="Review this problem"
                  submitLabel="Post review"
                  placeholder="Challenge the problem, refine it, or back up the framing…"
                />
              )}
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-xborder bg-xbg-secondary/40 p-5 shadow-[0_30px_80px_-55px_rgba(0,0,0,0.8)]">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-xtext-secondary">
                Solutions
              </p>
              <h2 className="mt-1 text-xl font-semibold">
                {question.answers.length} Answer{question.answers.length !== 1 && "s"}
              </h2>
              <p className="mt-1 text-sm text-xtext-secondary">
                Reviews stay attached to the solution they evaluate.
              </p>
            </div>
          </div>

          {user && (
            <div className="mt-5 rounded-2xl border border-dashed border-xborder bg-xbg/40 p-4">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
                Propose a solution
              </p>
              <AnswerForm questionId={question.id} onSubmitted={refreshQuestion} />
            </div>
          )}

          <div className="mt-5 space-y-4">
            {question.answers.map((a) => (
              <AnswerCard
                key={a.id}
                answer={a}
                onRefresh={refreshQuestion}
                onVoteAnswer={handleAnswerVote}
                onVoteComment={handleCommentVote}
              />
            ))}
            {question.answers.length === 0 && (
              <div className="rounded-2xl border border-dashed border-xborder px-4 py-6 text-sm text-xtext-secondary">
                No solutions yet. The first answer sets the baseline for review karma on this thread.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
