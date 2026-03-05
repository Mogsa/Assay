import Link from "next/link";
import type { QuestionSummary } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";

export function QuestionCard({ question }: { question: QuestionSummary }) {
  return (
    <div className="flex gap-4 border-b border-gray-200 py-4">
      <div className="flex w-24 shrink-0 flex-col items-end gap-1 text-sm">
        <span className={question.score > 0 ? "font-medium text-green-700" : "text-gray-500"}>
          {question.score} votes
        </span>
        <span
          className={
            question.answer_count > 0
              ? "rounded border border-green-600 px-1.5 text-green-700"
              : "text-gray-400"
          }
        >
          {question.answer_count} answers
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <Link
          href={`/questions/${question.id}`}
          className="text-base font-medium text-blue-700 hover:text-blue-500"
        >
          {question.title}
        </Link>
        <p className="mt-1 truncate text-sm text-gray-500">{question.body}</p>
        <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
          <span className="capitalize">{question.status}</span>
          <TimeAgo date={question.created_at} />
        </div>
      </div>
    </div>
  );
}
