"use client";

const STATUS_STYLES = {
  open: "border-xaccent/40 text-xaccent",
  answered: "border-xsuccess/40 text-xsuccess",
  resolved: "border-xborder text-xtext-secondary",
} as const;

export function QuestionStatusBadge({
  status,
}: {
  status: "open" | "answered" | "resolved";
}) {
  return (
    <span className={`rounded-full border px-2 py-0.5 text-[11px] uppercase tracking-[0.12em] ${STATUS_STYLES[status]}`}>
      {status}
    </span>
  );
}
