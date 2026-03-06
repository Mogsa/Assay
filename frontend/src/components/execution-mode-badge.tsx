"use client";

export function ExecutionModeBadge({
  mode,
  compact = false,
}: {
  mode: "manual" | "autonomous";
  compact?: boolean;
}) {
  const label = mode === "autonomous" ? "Autonomous" : "Manual";
  const classes = mode === "autonomous"
    ? "border-amber-400/30 bg-amber-400/10 text-amber-300"
    : "border-xborder bg-xbg-primary text-xtext-secondary";

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 font-medium ${
        compact ? "text-[10px] uppercase tracking-[0.16em]" : "text-xs"
      } ${classes}`}
    >
      {label}
    </span>
  );
}
