"use client";

import Link from "next/link";
import type { LinkInQuestion } from "@/lib/types";
import { AuthorChip } from "@/components/author-chip";

function relatedHref(link: LinkInQuestion) {
  if (link.source_type === "question" && link.source_question_id) {
    return `/questions/${link.source_question_id}`;
  }
  if (link.source_question_id && link.source_answer_id) {
    return `/questions/${link.source_question_id}#answer-${link.source_answer_id}`;
  }
  if (link.source_question_id) {
    return `/questions/${link.source_question_id}`;
  }
  return "#";
}

export function RelatedLinkCard({ link }: { link: LinkInQuestion }) {
  return (
    <Link
      href={relatedHref(link)}
      className="block rounded-xl border border-xborder bg-xbg-secondary p-3 transition-colors hover:bg-xbg-hover"
    >
      <div className="flex items-center gap-2 text-xs text-xtext-secondary">
        <span className="rounded-full bg-xbg-hover px-2 py-0.5 uppercase tracking-[0.12em]">
          {link.link_type === "repost" ? "Repost" : "Reference"}
        </span>
        <span>{link.source_type}</span>
      </div>
      {link.source_title && (
        <p className="mt-2 text-sm font-medium text-xtext-primary">{link.source_title}</p>
      )}
      {link.source_preview && (
        <p className="mt-1 text-sm text-xtext-secondary">{link.source_preview}</p>
      )}
      {link.source_author && (
        <div className="mt-2">
          <AuthorChip author={link.source_author} compact />
        </div>
      )}
    </Link>
  );
}
