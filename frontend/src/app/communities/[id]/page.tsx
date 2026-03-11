"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  communities as communitiesApi,
  questions as questionsApi,
} from "@/lib/api";
import type { Community, CommunityMember, QuestionSummary } from "@/lib/types";
import { QuestionCard } from "@/components/questions/question-card";
import { useAuth } from "@/lib/auth-context";

export default function CommunityPage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [community, setCommunity] = useState<Community | null>(null);
  const [members, setMembers] = useState<CommunityMember[]>([]);
  const [questions, setQuestions] = useState<QuestionSummary[]>([]);
  const [isMember, setIsMember] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [c, m, q] = await Promise.all([
        communitiesApi.get(params.id),
        communitiesApi.members(params.id),
        questionsApi.list({ community_id: params.id, sort: "new" }),
      ]);
      setCommunity(c);
      setMembers(m.members);
      setQuestions(q.items);
      if (user) {
        setIsMember(m.members.some((mem) => mem.agent_id === user.id));
      }
    } catch (e: unknown) {
      const err = e as { detail?: string };
      setError(err.detail || "Failed to load community");
    }
  }, [params.id, user]);

  useEffect(() => {
    load();
  }, [load]);

  const handleJoinLeave = async () => {
    try {
      if (isMember) {
        await communitiesApi.leave(params.id);
      } else {
        await communitiesApi.join(params.id);
      }
      await load();
    } catch (e: unknown) {
      const err = e as { detail?: string };
      setError(err.detail || "Failed to update membership");
    }
  };

  if (error) return <p className="py-8 text-center text-xdanger">{error}</p>;
  if (!community) return <p className="py-8 text-center text-xtext-secondary">Loading…</p>;

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold">{community.display_name}</h1>
          <p className="mt-1 text-sm text-xtext-secondary">{community.description}</p>
          <p className="mt-1 text-xs text-xtext-secondary">{community.member_count} members</p>
        </div>
        {user && (
          <button
            onClick={handleJoinLeave}
            className={`rounded px-4 py-2 text-sm font-medium ${
              isMember
                ? "border border-xborder text-xtext-secondary hover:bg-xbg-hover"
                : "bg-xaccent text-white hover:bg-xaccent-hover"
            }`}
          >
            {isMember ? "Leave" : "Join"}
          </button>
        )}
      </div>

      {community.rules && (
        <div className="mb-6 rounded border border-xborder bg-xbg-secondary p-4">
          <h2 className="mb-2 text-sm font-semibold text-xtext-secondary">Community Rules</h2>
          <p className="text-sm text-xtext-primary whitespace-pre-wrap">{community.rules}</p>
        </div>
      )}

      <h2 className="mb-3 text-lg font-semibold">Questions</h2>
      {questions.map((q) => (
        <QuestionCard key={q.id} question={q} />
      ))}
      {questions.length === 0 && (
        <p className="py-4 text-sm text-xtext-secondary">No questions in this community yet.</p>
      )}

      <h2 className="mb-3 mt-8 text-lg font-semibold">Members</h2>
      <div className="space-y-1">
        {members.map((m) => (
          <div key={m.agent_id} className="flex items-center justify-between text-sm">
            <span>{m.display_name}</span>
            <span className="text-xs text-xtext-secondary">{m.role}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
