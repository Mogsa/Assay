"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { questions as questionsApi, votes } from "@/lib/api";
import type { QuestionDetail } from "@/lib/types";
import { VoteButtons } from "@/components/questions/vote-buttons";
import { CommentList } from "@/components/questions/comment-list";
import { AnswerCard } from "@/components/questions/answer-card";
import { TimeAgo } from "@/components/ui/time-ago";
import Link from "next/link";

export default function QuestionPage() {
  const params = useParams<{ id: string }>();
  const [question, setQuestion] = useState<QuestionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    questionsApi
      .get(params.id)
      .then(setQuestion)
      .catch((e) => setError(e.detail || "Failed to load question"));
  }, [params.id]);

  if (error) return <p className="py-8 text-center text-red-500">{error}</p>;
  if (!question) return <p className="py-8 text-center text-gray-400">Loading…</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold">{question.title}</h1>
      <div className="mt-1 flex gap-4 text-sm text-gray-400">
        <span className="capitalize">{question.status}</span>
        <TimeAgo date={question.created_at} />
        <span>{question.answer_count} answers</span>
      </div>

      <div className="mt-4 flex gap-4">
        <VoteButtons
          score={question.score}
          onUpvote={() => votes.question(question.id, 1)}
          onDownvote={() => votes.question(question.id, -1)}
        />
        <div className="min-w-0 flex-1">
          <div className="whitespace-pre-wrap text-sm">{question.body}</div>
          <CommentList comments={question.comments} />
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold">
          {question.answers.length} Answer{question.answers.length !== 1 && "s"}
        </h2>
        {question.answers.map((a) => (
          <AnswerCard key={a.id} answer={a} />
        ))}
      </div>

      {question.related.length > 0 && (
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-gray-500">Related</h3>
          <div className="mt-2 space-y-1">
            {question.related.map((link) => (
              <div key={link.id} className="text-sm">
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500">
                  {link.link_type}
                </span>{" "}
                <Link
                  href={`/questions/${link.source_id}`}
                  className="text-blue-700 hover:text-blue-500"
                >
                  {link.source_id.slice(0, 8)}…
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
