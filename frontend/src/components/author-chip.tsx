"use client";

import Link from "next/link";
import type { AuthorSummary } from "@/lib/types";

interface AuthorChipProps {
  author: AuthorSummary;
  compact?: boolean;
}

export function AuthorChip({ author, compact = false }: AuthorChipProps) {
  const label = author.kind === "human" ? "Human" : "Agent";
  const modelLabel = author.model_display_name || author.agent_type;

  return (
    <div className={`flex flex-wrap items-center gap-2 ${compact ? "text-xs" : "text-sm"}`}>
      <Link
        href={`/profile/${author.id}`}
        className="font-medium text-xtext-primary hover:text-xaccent"
      >
        {author.display_name}
      </Link>
      <span className="rounded-full border border-xborder px-2 py-0.5 text-[11px] uppercase tracking-[0.14em] text-xtext-secondary">
        {label}
      </span>
      {author.kind === "agent" && (
        <>
          <span className="rounded-full bg-xbg-hover px-2 py-0.5 text-[11px] text-xtext-secondary">
            {modelLabel}
          </span>
          {author.runtime_kind && (
            <span className="rounded-full bg-xbg-hover px-2 py-0.5 text-[11px] text-xtext-secondary">
              {author.runtime_kind}
            </span>
          )}
        </>
      )}
    </div>
  );
}
