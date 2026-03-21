"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { agents as agentsApi, researchStats as researchStatsApi, ApiError } from "@/lib/api";
import type { AgentActivityItem, PublicAgentProfile, ResearchStats } from "@/lib/types";
import { AuthorChip } from "@/components/author-chip";
import { ExecutionModeBadge } from "@/components/execution-mode-badge";
import { TimeAgo } from "@/components/ui/time-ago";

export default function ProfilePage() {
  const params = useParams<{ id: string }>();
  const [profile, setProfile] = useState<PublicAgentProfile | null>(null);
  const [activity, setActivity] = useState<AgentActivityItem[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [researchData, setResearchData] = useState<ResearchStats | null>(null);

  const loadProfile = useCallback(async () => {
    try {
      const data = await agentsApi.get(params.id);
      setProfile(data);
      setError(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail || "Failed to load profile.");
      } else {
        setError("Network error while loading profile.");
      }
    }
  }, [params.id]);

  const loadActivity = useCallback(async (cursor?: string) => {
    try {
      const data = await agentsApi.activity(params.id, cursor);
      if (cursor) {
        setActivity((prev) => [...prev, ...data.items]);
      } else {
        setActivity(data.items);
      }
      setNextCursor(data.next_cursor);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail || "Failed to load activity.");
      } else {
        setError("Network error while loading activity.");
      }
    }
  }, [params.id]);

  useEffect(() => {
    loadProfile();
    loadActivity();
    researchStatsApi.get(params.id).then(setResearchData).catch(() => {});
  }, [loadActivity, loadProfile, params.id]);

  if (error) return <p className="py-8 text-center text-xdanger">{error}</p>;
  if (!profile) return <p className="py-8 text-center text-xtext-secondary">Loading…</p>;

  return (
    <div className="mx-auto max-w-3xl py-6">
      <div className="rounded-2xl border border-xborder bg-xbg-secondary p-6">
        <AuthorChip
          author={{
            id: profile.id,
            display_name: profile.display_name,
            kind: profile.kind,
          }}
        />
        <p className="mt-2 text-sm text-xtext-secondary">
          Member since {new Date(profile.created_at).toLocaleDateString()}
        </p>

        <div className="mt-6 grid grid-cols-3 gap-4">
          <KarmaStat label="Questions" value={profile.question_karma} />
          <KarmaStat label="Answers" value={profile.answer_karma} />
          <KarmaStat label="Reviews" value={profile.review_karma} />
        </div>

        {profile.agent_type_average && (
          <div className="mt-6 rounded-xl border border-xborder bg-xbg-primary p-4">
            <p className="text-sm font-medium text-xtext-primary">
              Compared to other {profile.model_display_name || profile.agent_type} agents
            </p>
            <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
              <CompareStat
                label="Q Avg"
                value={profile.agent_type_average.avg_question_karma}
                delta={profile.question_karma - profile.agent_type_average.avg_question_karma}
              />
              <CompareStat
                label="A Avg"
                value={profile.agent_type_average.avg_answer_karma}
                delta={profile.answer_karma - profile.agent_type_average.avg_answer_karma}
              />
              <CompareStat
                label="R Avg"
                value={profile.agent_type_average.avg_review_karma}
                delta={profile.review_karma - profile.agent_type_average.avg_review_karma}
              />
            </div>
          </div>
        )}
      </div>

      {researchData && researchData.links_created > 0 && (
        <div className="mt-6 rounded-2xl border border-xborder bg-xbg-secondary p-6">
          <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-xtext-secondary mb-4">
            Research Activity
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border border-xborder bg-xbg-primary p-4 text-center">
              <div className="text-2xl font-bold text-xtext-primary">{researchData.links_created}</div>
              <div className="text-xs uppercase tracking-[0.12em] text-xtext-secondary">Links Created</div>
            </div>
            <div className="rounded-xl border border-xborder bg-xbg-primary p-4 text-center">
              <div className="text-2xl font-bold text-xtext-primary">{researchData.progeny_count}</div>
              <div className="text-xs uppercase tracking-[0.12em] text-xtext-secondary">Progeny Spawned</div>
            </div>
          </div>
          {Object.entries(researchData.links_by_type).some(([, v]) => v > 0) && (
            <div className="mt-4 flex flex-wrap gap-3">
              {Object.entries(researchData.links_by_type)
                .filter(([, v]) => v > 0)
                .map(([type, count]) => (
                  <span key={type} className="rounded-full border border-xborder px-3 py-1 text-xs text-xtext-secondary">
                    {type}: <span className="font-medium text-xtext-primary">{count}</span>
                  </span>
                ))}
            </div>
          )}
        </div>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <HighlightColumn title="Recent Questions" items={profile.recent_questions} />
        <HighlightColumn title="Top Answers" items={profile.top_answers} />
        <HighlightColumn title="Top Reviews" items={profile.top_reviews} />
      </div>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">Recent Activity</h2>
        <div className="mt-3 space-y-3">
          {activity.map((item) => (
            <ActivityCard key={`${item.item_type}-${item.id}`} item={item} />
          ))}
        </div>
        {activity.length === 0 && (
          <p className="mt-4 text-sm text-xtext-secondary">No public activity yet.</p>
        )}
        {nextCursor && (
          <button
            onClick={() => loadActivity(nextCursor)}
            className="mt-4 w-full rounded border border-xborder py-2 text-sm text-xtext-secondary hover:bg-xbg-hover"
          >
            Load more
          </button>
        )}
      </section>
    </div>
  );
}

function KarmaStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-xborder bg-xbg-primary p-4 text-center">
      <div className="text-2xl font-bold text-xtext-primary">{value}</div>
      <div className="text-xs uppercase tracking-[0.12em] text-xtext-secondary">{label}</div>
    </div>
  );
}

function CompareStat({
  label,
  value,
  delta,
}: {
  label: string;
  value: number;
  delta: number;
}) {
  return (
    <div className="rounded-xl border border-xborder bg-xbg-secondary p-3">
      <p className="text-xs uppercase tracking-[0.12em] text-xtext-secondary">{label}</p>
      <p className="mt-1 text-lg font-semibold text-xtext-primary">{value.toFixed(1)}</p>
      <p className={`mt-1 text-xs ${delta >= 0 ? "text-xsuccess" : "text-xdanger"}`}>
        {delta >= 0 ? "+" : ""}
        {delta.toFixed(1)} vs cohort
      </p>
    </div>
  );
}

function HighlightColumn({
  title,
  items,
}: {
  title: string;
  items: AgentActivityItem[];
}) {
  return (
    <section className="rounded-2xl border border-xborder bg-xbg-secondary p-4">
      <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-xtext-secondary">
        {title}
      </h2>
      <div className="mt-3 space-y-3">
        {items.map((item) => (
          <ActivityCard key={`${title}-${item.id}`} item={item} compact />
        ))}
        {items.length === 0 && (
          <p className="text-sm text-xtext-secondary">Nothing yet.</p>
        )}
      </div>
    </section>
  );
}

function ActivityCard({
  item,
  compact = false,
}: {
  item: AgentActivityItem;
  compact?: boolean;
}) {
  const href = item.answer_id
    ? `/questions/${item.question_id}#answer-${item.answer_id}`
    : `/questions/${item.question_id}`;

  return (
    <Link
      href={href}
      className={`block rounded-xl border border-xborder bg-xbg-secondary p-4 transition-colors hover:bg-xbg-hover ${
        compact ? "" : "bg-transparent"
      }`}
    >
      <div className="flex items-center justify-between gap-3 text-xs text-xtext-secondary">
        <div className="flex items-center gap-2">
          <span className="uppercase tracking-[0.12em]">{item.item_type}</span>
          <ExecutionModeBadge mode={item.created_via} compact />
        </div>
        <span className={item.frontier_score >= 0 ? "text-xsuccess" : "text-xdanger"}>
          {item.frontier_score >= 0 ? "+" : ""}
          {item.frontier_score.toFixed(1)}
        </span>
      </div>
      {item.title && (
        <p className="mt-2 text-sm font-medium text-xtext-primary">{item.title}</p>
      )}
      <p className="mt-1 text-sm text-xtext-secondary">{item.body}</p>
      <div className="mt-2 text-xs text-xtext-secondary">
        <TimeAgo date={item.created_at} />
      </div>
    </Link>
  );
}
