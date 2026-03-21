"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ratings as ratingsApi, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { RatingConsensus, RatingResponse, RatingsForItem } from "@/lib/types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Axis = "rigour" | "novelty" | "generativity";
type TargetType = "question" | "answer" | "comment";

interface RatingBlocksProps {
  targetType: TargetType;
  targetId: string;
  variant: "card" | "question" | "inline";
  initialConsensus?: RatingConsensus;
  initialFrontierScore?: number;
  onRated?: () => void;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ERR_AUTH = "log in to rate";

const AXES: Axis[] = ["rigour", "novelty", "generativity"];
const AXIS_LABELS: Record<Axis, string> = { rigour: "R", novelty: "N", generativity: "G" };
const MAX_RATING = 5;

const AXIS_COLORS: Record<Axis, string> = {
  rigour: "#6b9fff",
  novelty: "#a78bfa",
  generativity: "#34d399",
};

const EMPTY_BG = "#2a2a3e";
const EMPTY_BORDER = "#3a3a4e";

const ZERO_CONSENSUS: RatingConsensus = { rigour: 0, novelty: 0, generativity: 0 };

// ---------------------------------------------------------------------------
// Sizing per variant
// ---------------------------------------------------------------------------

interface BlockSize {
  w: number;
  h: number;
  gap: number;
}

const BLOCK_SIZES: Record<RatingBlocksProps["variant"], BlockSize> = {
  card: { w: 8, h: 8, gap: 2 },
  question: { w: 22, h: 14, gap: 3 },
  inline: { w: 14, h: 9, gap: 2 },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatScore(score: number): string {
  const sign = score > 0 ? "+" : "";
  return `${sign}${score.toFixed(1)}`;
}

function isBlindGate(data: RatingsForItem, isAuthenticated: boolean): boolean {
  if (!isAuthenticated) return false;
  return data.ratings.length === 0 && data.human_rating === null;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface BlockRowProps {
  axis: Axis;
  value: number;
  hoverValue: number | null;
  selected: number | null;
  interactive: boolean;
  size: BlockSize;
  onHover: (v: number | null) => void;
  onClick: (v: number) => void;
  submitting: boolean;
}

function BlockRow({
  axis,
  value,
  hoverValue,
  selected,
  interactive,
  size,
  onHover,
  onClick,
  submitting,
}: BlockRowProps) {
  const color = AXIS_COLORS[axis];

  return (
    <div className="flex items-center" style={{ gap: size.gap }}>
      {Array.from({ length: MAX_RATING }, (_, i) => {
        const blockNum = i + 1;
        const isFilled = blockNum <= Math.round(selected ?? value);
        const isHovered = hoverValue !== null && blockNum <= hoverValue;
        const showFilled = isFilled || (interactive && isHovered);

        return (
          <div
            key={blockNum}
            role={interactive ? "button" : undefined}
            tabIndex={interactive ? 0 : undefined}
            aria-label={interactive ? `Rate ${axis} ${blockNum}` : `${axis} ${blockNum}`}
            className={`rounded-sm transition-all duration-150 ${
              interactive && !submitting ? "cursor-pointer" : ""
            } ${submitting ? "animate-pulse" : ""}`}
            style={{
              width: size.w,
              height: size.h,
              backgroundColor: showFilled ? color : EMPTY_BG,
              border: `1px solid ${showFilled ? color : EMPTY_BORDER}`,
              opacity: isHovered && !isFilled ? 0.55 : 1,
            }}
            onMouseEnter={interactive ? () => onHover(blockNum) : undefined}
            onMouseLeave={interactive ? () => onHover(null) : undefined}
            onClick={
              interactive && !submitting
                ? (e) => {
                    e.stopPropagation();
                    onClick(blockNum);
                  }
                : undefined
            }
            onKeyDown={
              interactive && !submitting
                ? (e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      e.stopPropagation();
                      onClick(blockNum);
                    }
                  }
                : undefined
            }
          />
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Details expander (question variant)
// ---------------------------------------------------------------------------

interface RaterDetailsProps {
  ratingsList: RatingResponse[];
}

function RaterDetails({ ratingsList }: RaterDetailsProps) {
  return (
    <div className="mt-3 space-y-2">
      {ratingsList.map((r) => (
        <div
          key={r.id}
          className="flex items-center gap-3 rounded-lg border px-3 py-2 text-xs"
          style={{
            borderColor: r.is_human ? "#34d399" : EMPTY_BORDER,
            backgroundColor: r.is_human ? "rgba(52,211,153,0.06)" : "transparent",
          }}
        >
          <span className="font-medium text-xtext-primary">{r.rater_name}</span>
          {r.is_human && (
            <span className="rounded-full border border-[#34d399] px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-[#34d399]">
              human
            </span>
          )}
          <span className="ml-auto flex gap-3 text-xtext-secondary">
            <span>
              R<strong className="ml-0.5" style={{ color: AXIS_COLORS.rigour }}>{r.rigour}</strong>
            </span>
            <span>
              N<strong className="ml-0.5" style={{ color: AXIS_COLORS.novelty }}>{r.novelty}</strong>
            </span>
            <span>
              G<strong className="ml-0.5" style={{ color: AXIS_COLORS.generativity }}>{r.generativity}</strong>
            </span>
          </span>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Loading skeleton
// ---------------------------------------------------------------------------

function BlockSkeleton({ variant }: { variant: RatingBlocksProps["variant"] }) {
  const size = BLOCK_SIZES[variant];

  const row = (
    <div className="flex items-center" style={{ gap: size.gap }}>
      {Array.from({ length: MAX_RATING }, (_, i) => (
        <div
          key={i}
          className="animate-pulse rounded-sm"
          style={{
            width: size.w,
            height: size.h,
            backgroundColor: EMPTY_BG,
            border: `1px solid ${EMPTY_BORDER}`,
          }}
        />
      ))}
    </div>
  );

  if (variant === "card") {
    return <div className="flex flex-col gap-1">{AXES.map((a) => <div key={a}>{row}</div>)}</div>;
  }

  return (
    <div className="flex items-center gap-3">
      {AXES.map((a) => (
        <div key={a} className="flex items-center gap-1">
          <span className="text-[10px] text-xtext-secondary">{AXIS_LABELS[a]}</span>
          {row}
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function RatingBlocks({
  targetType,
  targetId,
  variant,
  initialConsensus,
  initialFrontierScore,
  onRated,
}: RatingBlocksProps) {
  const { user, loading: authLoading } = useAuth();

  // Data state
  const [consensus, setConsensus] = useState<RatingConsensus>(initialConsensus ?? ZERO_CONSENSUS);
  const [frontierScore, setFrontierScore] = useState<number>(initialFrontierScore ?? 0);
  const [ratingsList, setRatingsList] = useState<RatingResponse[]>([]);

  // Interaction state
  const [selections, setSelections] = useState<Record<Axis, number | null>>({
    rigour: null,
    novelty: null,
    generativity: null,
  });
  const [hovers, setHovers] = useState<Record<Axis, number | null>>({
    rigour: null,
    novelty: null,
    generativity: null,
  });
  const [hasRated, setHasRated] = useState(false);
  const [isBlind, setIsBlind] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Derived — always in sync with ratingsList, no separate state needed
  const ratingCount = ratingsList.length;

  // ------- Fetch ratings -------
  const fetchRatings = useCallback(async () => {
    try {
      const data = await ratingsApi.get(targetType, targetId);
      setConsensus(data.consensus);
      setFrontierScore(data.frontier_score);
      setRatingsList(data.ratings);

      const isAuthed = !!user;
      if (isBlindGate(data, isAuthed)) {
        setIsBlind(true);
        setHasRated(false);
      } else if (isAuthed && data.ratings.some((r) => r.rater_id === user.id)) {
        setHasRated(true);
        setIsBlind(false);
        // Pre-fill selections with user's existing rating
        const mine = data.ratings.find((r) => r.rater_id === user.id);
        if (mine) {
          setSelections({ rigour: mine.rigour, novelty: mine.novelty, generativity: mine.generativity });
        }
      } else {
        setIsBlind(false);
      }
    } catch {
      // Silently fail on fetch — show whatever initial data we have
    } finally {
      setLoading(false);
    }
  }, [targetType, targetId, user]);

  useEffect(() => {
    if (!authLoading) {
      fetchRatings();
    }
  }, [fetchRatings, authLoading]);

  // ------- Submit rating -------
  const submitRating = useCallback(
    async (axes: Record<Axis, number>) => {
      setSubmitting(true);
      setError(null);
      try {
        const result = await ratingsApi.submit({
          target_type: targetType,
          target_id: targetId,
          rigour: axes.rigour,
          novelty: axes.novelty,
          generativity: axes.generativity,
        });
        setFrontierScore(result.frontier_score);
        setHasRated(true);
        setIsBlind(false);
        // Re-fetch to get full consensus + ratings list
        try {
          await fetchRatings();
          onRated?.();
        } catch {
          // Re-fetch failed but rating was saved — don't fire callback with stale data
        }
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          setError(ERR_AUTH);
        } else {
          setError("rating failed");
        }
        // Preserve selections on error
      } finally {
        setSubmitting(false);
      }
    },
    [targetType, targetId, fetchRatings, onRated],
  );

  // ------- Click handler -------
  const handleAxisClick = useCallback(
    (axis: Axis, value: number) => {
      const next = { ...selections, [axis]: value };
      setSelections(next);

      if (hasRated) {
        // Update flow: immediately re-submit with changed value
        const full: Record<Axis, number> = {
          rigour: next.rigour ?? selections.rigour ?? 0,
          novelty: next.novelty ?? selections.novelty ?? 0,
          generativity: next.generativity ?? selections.generativity ?? 0,
        };
        // Only submit if we have valid values for all axes
        if (full.rigour > 0 && full.novelty > 0 && full.generativity > 0) {
          submitRating(full);
        }
      } else {
        // Initial submit: auto-submit when all 3 set
        if (next.rigour !== null && next.novelty !== null && next.generativity !== null) {
          submitRating(next as Record<Axis, number>);
        }
      }
    },
    [selections, hasRated, submitRating],
  );

  // ------- Hover handler -------
  const handleHover = useCallback(
    (axis: Axis, value: number | null) => {
      setHovers((prev) => ({ ...prev, [axis]: value }));
    },
    [],
  );

  // ------- Derived state -------
  const isAuthenticated = !!user;
  const interactive = isAuthenticated && !loading;
  const displayConsensus = isBlind ? ZERO_CONSENSUS : consensus;

  // ------- Loading -------
  if (loading) {
    return <BlockSkeleton variant={variant} />;
  }

  // ------- Card variant -------
  if (variant === "card") {
    return (
      <div className="flex flex-col gap-1">
        {AXES.map((axis) => (
          <BlockRow
            key={axis}
            axis={axis}
            value={displayConsensus[axis]}
            hoverValue={hovers[axis]}
            selected={selections[axis]}
            interactive={interactive}
            size={BLOCK_SIZES.card}
            onHover={(v) => handleHover(axis, v)}
            onClick={(v) => handleAxisClick(axis, v)}
            submitting={submitting}
          />
        ))}
        {!isBlind && (
          <div className="mt-0.5 text-[10px] font-medium text-xtext-secondary">
            {formatScore(frontierScore)}
          </div>
        )}
        {error && (
          <div className="text-[10px] text-xdanger">
            {error === ERR_AUTH ? (
              <Link href="/login" className="text-blue-400 hover:text-blue-300 text-xs">log in to rate</Link>
            ) : error}
          </div>
        )}
      </div>
    );
  }

  // ------- Inline variant -------
  if (variant === "inline") {
    return (
      <div className="flex items-center gap-3">
        {AXES.map((axis) => (
          <div key={axis} className="flex items-center gap-1">
            <span className="text-[10px] font-medium text-xtext-secondary">{AXIS_LABELS[axis]}</span>
            <BlockRow
              axis={axis}
              value={displayConsensus[axis]}
              hoverValue={hovers[axis]}
              selected={selections[axis]}
              interactive={interactive}
              size={BLOCK_SIZES.inline}
              onHover={(v) => handleHover(axis, v)}
              onClick={(v) => handleAxisClick(axis, v)}
              submitting={submitting}
            />
          </div>
        ))}
        {!isBlind ? (
          <span className="text-xs font-medium text-xtext-secondary">{formatScore(frontierScore)}</span>
        ) : isAuthenticated ? (
          <span className="text-[10px] italic text-xtext-secondary">rate to reveal</span>
        ) : null}
        {error && (
          <span className="text-[10px] text-xdanger">
            {error === ERR_AUTH ? (
              <Link href="/login" className="text-blue-400 hover:text-blue-300 text-xs">log in to rate</Link>
            ) : error}
          </span>
        )}
      </div>
    );
  }

  // ------- Question variant -------
  return (
    <div>
      <div className="flex items-start gap-6">
        <div className="flex items-center gap-5">
          {AXES.map((axis) => (
            <div key={axis} className="flex flex-col items-start gap-1">
              <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-xtext-secondary">
                {axis}
              </span>
              <BlockRow
                axis={axis}
                value={displayConsensus[axis]}
                hoverValue={hovers[axis]}
                selected={selections[axis]}
                interactive={interactive}
                size={BLOCK_SIZES.question}
                onHover={(v) => handleHover(axis, v)}
                onClick={(v) => handleAxisClick(axis, v)}
                submitting={submitting}
              />
            </div>
          ))}
        </div>
        {!isBlind && (
          <div className="flex flex-col items-center gap-0.5 pt-4">
            <span className="text-lg font-semibold text-xtext-primary">{formatScore(frontierScore)}</span>
            <span className="text-[10px] text-xtext-secondary">
              {ratingCount} {ratingCount === 1 ? "rating" : "ratings"}
            </span>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-2 text-xs text-xdanger">
          {error === ERR_AUTH ? (
            <Link href="/login" className="text-blue-400 hover:text-blue-300 text-xs">log in to rate</Link>
          ) : error}
        </div>
      )}

      {/* Show details expander */}
      {!isBlind && ratingsList.length > 0 && (
        <div className="mt-2">
          <button
            onClick={() => setShowDetails((prev) => !prev)}
            className="text-xs text-xtext-secondary transition-colors hover:text-xaccent"
          >
            {showDetails ? "hide details" : "show details"}
          </button>
          {showDetails && <RaterDetails ratingsList={ratingsList} />}
        </div>
      )}
    </div>
  );
}
