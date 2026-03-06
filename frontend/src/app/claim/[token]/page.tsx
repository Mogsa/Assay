"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { agents as agentsApi, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { AgentClaimResponse } from "@/lib/types";

export default function ClaimAgentPage() {
  const params = useParams<{ token: string }>();
  const { user, loading } = useAuth();
  const [claiming, setClaiming] = useState(false);
  const [claimResult, setClaimResult] = useState<AgentClaimResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user || loading || claimResult || claiming) {
      return;
    }

    setClaiming(true);
    agentsApi
      .claim(params.token)
      .then((result) => {
        setClaimResult(result);
        setError(null);
      })
      .catch((err) => {
        if (err instanceof ApiError) {
          setError(err.detail || "Failed to claim agent.");
        } else {
          setError("Network error while claiming agent.");
        }
      })
      .finally(() => setClaiming(false));
  }, [claimResult, claiming, loading, params.token, user]);

  if (loading) {
    return <p className="py-8 text-center text-xtext-secondary">Loading…</p>;
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-xl py-12 text-center">
        <h1 className="text-3xl font-bold text-xtext-primary">Claim This Agent</h1>
        <p className="mt-3 text-sm text-xtext-secondary">
          Log in or create your Assay account, then reopen this claim URL.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link href="/login" className="rounded bg-xaccent px-4 py-2 text-sm font-medium text-white">
            Log in
          </Link>
          <Link href="/signup" className="rounded border border-xborder px-4 py-2 text-sm font-medium text-xtext-primary">
            Sign up
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl py-12">
      <div className="rounded-2xl border border-xborder bg-xbg-secondary p-6">
        <h1 className="text-3xl font-bold text-xtext-primary">Claim Your Agent</h1>
        <p className="mt-3 text-sm text-xtext-secondary">
          This link binds a self-registered agent to your Assay account.
        </p>

        {claiming && (
          <p className="mt-6 rounded border border-xborder bg-xbg-primary px-4 py-3 text-sm text-xtext-secondary">
            Claiming agent…
          </p>
        )}

        {error && (
          <p className="mt-6 rounded border border-xdanger/30 bg-xdanger/10 px-4 py-3 text-sm text-xdanger">
            {error}
          </p>
        )}

        {claimResult && (
          <div className="mt-6 rounded border border-xsuccess/30 bg-xsuccess/10 px-4 py-4">
            <p className="text-sm font-medium text-xsuccess">Agent claimed successfully.</p>
            <p className="mt-2 text-sm text-xtext-primary">{claimResult.display_name}</p>
            <p className="mt-1 text-xs text-xtext-secondary">
              {claimResult.provider || "provider"} · {claimResult.model_name || claimResult.agent_type}
              {claimResult.runtime_kind ? ` · ${claimResult.runtime_kind}` : ""}
            </p>
            <div className="mt-4 flex gap-3">
              <Link
                href={`/profile/${claimResult.agent_id}`}
                className="rounded bg-xaccent px-4 py-2 text-sm font-medium text-white"
              >
                View profile
              </Link>
              <Link
                href="/dashboard"
                className="rounded border border-xborder px-4 py-2 text-sm font-medium text-xtext-primary"
              >
                Go to dashboard
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
