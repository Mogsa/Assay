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
import Link from "next/link";

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

  const relatedHref = (sourceType: string, sourceId: string, sourceQuestionId?: string | null) => {
    if (sourceType === "question") return `/questions/${sourceId}`;
    if (sourceQuestionId) return `/questions/${sourceQuestionId}#answer-${sourceId}`;
    return "#";
  };

  return (
    <div>
      <h1 className="text-2xl font-bold">{question.title}</h1>
      <div className="mt-1 flex gap-4 text-sm text-xtext-secondary">
        <span className="capitalize">{question.status}</span>
        <TimeAgo date={question.created_at} />
        <span>{question.answer_count} answers</span>
      </div>

      <div className="mt-4 flex gap-4">
        <VoteButtons
          score={question.score}
          viewerVote={question.viewer_vote}
          onVote={handleQuestionVote}
        />
        <div className="min-w-0 flex-1">
          <div className="whitespace-pre-wrap text-sm">{question.body}</div>
          <CommentList comments={question.comments} onVoteComment={handleCommentVote} />
          {user && (
            <CommentForm
              targetType="question"
              targetId={question.id}
              onSubmitted={refreshQuestion}
            />
          )}
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold">
          {question.answers.length} Answer{question.answers.length !== 1 && "s"}
        </h2>
        {question.answers.map((a) => (
          <AnswerCard
            key={a.id}
            answer={a}
            onRefresh={refreshQuestion}
            onVoteAnswer={handleAnswerVote}
            onVoteComment={handleCommentVote}
          />
        ))}
      </div>

      {user && (
        <AnswerForm questionId={question.id} onSubmitted={refreshQuestion} />
      )}

      {question.related.length > 0 && (
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-xtext-secondary">Related</h3>
          <div className="mt-2 space-y-1">
            {question.related.map((link) => (
              <div key={link.id} className="text-sm">
                <span className="rounded bg-xbg-hover px-1.5 py-0.5 text-xs text-xtext-secondary">
                  {link.link_type}
                </span>{" "}
                <Link
                  href={relatedHref(link.source_type, link.source_id, link.source_question_id)}
                  className="text-xaccent hover:text-xaccent"
                >
                  {link.source_id.slice(0, 8)}\u2026
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
