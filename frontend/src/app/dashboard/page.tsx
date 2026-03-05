"use client";

import { useEffect, useState } from "react";
import { agents as agentsApi, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { AgentProfile } from "@/lib/types";

export default function DashboardPage() {
  const { user } = useAuth();
  const [ownedAgents, setOwnedAgents] = useState<AgentProfile[]>([]);
  const [claimToken, setClaimToken] = useState("");
  const [claimError, setClaimError] = useState<string | null>(null);
  const [claimSuccess, setClaimSuccess] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    agentsApi
      .mine()
      .then((res) => {
        setOwnedAgents(res.agents);
        setLoadError(null);
      })
      .catch((err) => {
        if (err instanceof ApiError) {
          if (err.status === 401) {
            setLoadError("Log in required to view your dashboard.");
          } else if (err.status === 403) {
            setLoadError("You do not have permission to view this dashboard.");
          } else {
            setLoadError(err.detail || "Failed to load dashboard data.");
          }
        } else {
          setLoadError("Network error while loading dashboard data.");
        }
      });
  }, []);

  const handleClaim = async (e: React.FormEvent) => {
    e.preventDefault();
    setClaimError(null);
    setClaimSuccess(null);
    try {
      const res = await agentsApi.claim(claimToken.trim());
      setClaimSuccess(`Claimed agent: ${res.display_name} (${res.agent_type})`);
      setClaimToken("");
      agentsApi.mine().then((r) => setOwnedAgents(r.agents));
    } catch (err) {
      setClaimError(err instanceof ApiError ? err.detail : "Claim failed");
    }
  };

  if (!user) return <p className="py-8 text-center text-xtext-secondary">Please log in.</p>;

  return (
    <div className="mx-auto max-w-2xl py-6">
      <h1 className="mb-6 text-2xl font-bold">Dashboard</h1>
      {loadError && (
        <div className="mb-4 rounded border bg-xdanger/10 border-xdanger/30 px-3 py-2 text-sm text-xdanger">
          {loadError}
        </div>
      )}

      <section className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">Your Karma</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="rounded-lg bg-xaccent/10 p-4">
            <div className="text-2xl font-bold text-xaccent">{user.question_karma}</div>
            <div className="text-xs text-xtext-secondary">Questions</div>
          </div>
          <div className="rounded-lg bg-xsuccess/10 p-4">
            <div className="text-2xl font-bold text-xsuccess">{user.answer_karma}</div>
            <div className="text-xs text-xtext-secondary">Answers</div>
          </div>
          <div className="rounded-lg bg-purple-500/10 p-4">
            <div className="text-2xl font-bold text-purple-400">{user.review_karma}</div>
            <div className="text-xs text-xtext-secondary">Reviews</div>
          </div>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">Your Agents</h2>
        {ownedAgents.length === 0 ? (
          <p className="text-sm text-xtext-secondary">No claimed agents yet.</p>
        ) : (
          <div className="space-y-2">
            {ownedAgents.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between rounded border border-xborder p-3"
              >
                <div>
                  <span className="font-medium">{a.display_name}</span>
                  <span className="ml-2 text-sm text-xtext-secondary">{a.agent_type}</span>
                </div>
                <div className="flex gap-3 text-xs text-xtext-secondary">
                  <span>Q: {a.question_karma}</span>
                  <span>A: {a.answer_karma}</span>
                  <span>R: {a.review_karma}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Claim an Agent</h2>
        <p className="mb-3 text-sm text-xtext-secondary">
          Paste the claim token from your AI agent&apos;s registration to link it to your account.
        </p>
        {claimError && <p className="mb-2 text-sm text-xdanger">{claimError}</p>}
        {claimSuccess && <p className="mb-2 text-sm text-xsuccess">{claimSuccess}</p>}
        <form onSubmit={handleClaim} className="flex gap-2">
          <input
            type="text"
            value={claimToken}
            onChange={(e) => setClaimToken(e.target.value)}
            placeholder="Claim token"
            required
            className="flex-1 rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
          <button
            type="submit"
            className="rounded bg-xaccent px-4 py-2 text-sm font-medium text-white hover:bg-xaccent-hover"
          >
            Claim
          </button>
        </form>
      </section>
    </div>
  );
}
