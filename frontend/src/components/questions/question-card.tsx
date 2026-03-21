import Link from "next/link";
import type { QuestionSummary } from "@/lib/types";
import { TimeAgo } from "@/components/ui/time-ago";
import { AuthorChip } from "@/components/author-chip";
import { QuestionStatusBadge } from "@/components/question-status-badge";

export function QuestionCard({ question }: { question: QuestionSummary }) {
  return (
    <div className="flex gap-4 border-b border-xborder py-4">
      <div className="flex w-24 shrink-0 flex-col items-end gap-1 text-sm">
        <span className={question.frontier_score > 0 ? "font-medium text-xsuccess" : "text-xtext-secondary"}>
          {question.frontier_score.toFixed(1)}
        </span>
        <span
          className={
            question.answer_count > 0
              ? "rounded border border-xsuccess px-1.5 text-xsuccess"
              : "text-xtext-secondary"
          }
        >
          {question.answer_count} answers
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <Link
          href={`/questions/${question.id}`}
          className="text-base font-medium text-xaccent hover:text-xaccent"
        >
          {question.title}
        </Link>
        <p className="mt-1 text-sm text-xtext-secondary">{question.body}</p>
        <div className="mt-2">
          <AuthorChip author={question.author} compact />
        </div>
        <div className="mt-2 flex items-center gap-3 text-xs text-xtext-secondary">
          <QuestionStatusBadge status={question.status} />
          <TimeAgo date={question.created_at} />
        </div>
      </div>
    </div>
  );
}
