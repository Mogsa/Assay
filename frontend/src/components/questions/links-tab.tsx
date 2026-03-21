"use client";

import Link from "next/link";
import type { LinkInQuestion } from "@/lib/types";
import { AuthorChip } from "@/components/author-chip";
import { TimeAgo } from "@/components/ui/time-ago";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BORDER_COLORS: Record<LinkInQuestion["link_type"], string> = {
  extends: "#f59e0b",
  contradicts: "#ef4444",
  references: "#888888",
};

const LABEL_COLORS: Record<LinkInQuestion["link_type"], string> = {
  extends: "text-amber-400",
  contradicts: "text-red-400",
  references: "text-gray-400",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function relatedHref(link: LinkInQuestion): string {
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

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface LinksTabProps {
  links: LinkInQuestion[];
}

export function LinksTab({ links }: LinksTabProps) {
  if (links.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-xtext-secondary">
        No links yet.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {links.map((link) => (
        <div
          key={link.id}
          className="rounded-xl border border-xborder bg-xbg-secondary p-3"
          style={{ borderLeftWidth: 3, borderLeftColor: BORDER_COLORS[link.link_type] }}
        >
          <div className="flex items-center gap-2 text-xs">
            <span className={`font-semibold uppercase tracking-[0.12em] ${LABEL_COLORS[link.link_type]}`}>
              {link.link_type}
            </span>
            {link.source_author && <AuthorChip author={link.source_author} compact />}
            <span className="text-xtext-secondary">
              <TimeAgo date={link.created_at} />
            </span>
          </div>

          {link.source_title && (
            <Link
              href={relatedHref(link)}
              className="mt-2 block text-sm font-medium text-xtext-primary hover:text-xaccent transition-colors"
            >
              {link.source_title}
            </Link>
          )}

          {link.source_preview && !link.source_title && (
            <Link
              href={relatedHref(link)}
              className="mt-2 block text-sm text-xtext-secondary hover:text-xaccent transition-colors"
            >
              {link.source_preview}
            </Link>
          )}

          {link.reason && (link.link_type === "extends" || link.link_type === "contradicts") && (
            <div className="mt-2 rounded-lg bg-xbg/60 px-3 py-2 text-xs text-xtext-secondary">
              {link.reason}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
