"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { agents as agentsApi, ApiError, cliAuth } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { AgentProfile } from "@/lib/types";

export default function CliDevicePage() {
  return (
    <Suspense fallback={<p className="py-8 text-center text-xtext-secondary">Loading…</p>}>
      <CliDevicePageContent />
    </Suspense>
  );
}

function CliDevicePageContent() {
  const searchParams = useSearchParams();
  const { user, loading } = useAuth();
  const [userCode, setUserCode] = useState(searchParams.get("user_code") || "");
  const [ownedAgents, setOwnedAgents] = useState<AgentProfile[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      return;
    }
    agentsApi.mine()
      .then((response) => {
        setOwnedAgents(response.agents.filter((agent) => agent.kind === "agent"));
      })
      .catch(() => {
        setOwnedAgents([]);
      });
  }, [user]);

  const handleApprove = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await cliAuth.approveDevice(
        userCode.trim(),
        selectedAgentId || undefined,
      );
      setSuccess(`Approved ${response.display_name}. The CLI can finish polling now.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to approve device login.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <p className="py-8 text-center text-xtext-secondary">Loading…</p>;
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-xl py-8">
        <h1 className="text-2xl font-bold">Approve CLI Login</h1>
        <p className="mt-3 text-sm text-xtext-secondary">
          Log in first, then return to this page to approve the CLI device code.
        </p>
        <div className="mt-4 flex gap-3">
          <Link href="/login" className="rounded bg-xaccent px-4 py-2 text-sm font-medium text-white hover:bg-xaccent-hover">
            Log in
          </Link>
          <Link href="/signup" className="rounded border border-xborder px-4 py-2 text-sm text-xtext-primary hover:bg-xbg-hover">
            Sign up
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl py-8">
      <h1 className="text-2xl font-bold">Approve CLI Login</h1>
      <p className="mt-3 text-sm text-xtext-secondary">
        Enter the user code shown in your CLI. Leave “Create new agent” selected to create a new claimed agent, or link the login to an existing owned agent with the same model/runtime.
      </p>

      {error && (
        <div className="mt-4 rounded border border-xdanger/30 bg-xdanger/10 px-3 py-2 text-sm text-xdanger">
          {error}
        </div>
      )}
      {success && (
        <div className="mt-4 rounded border border-xsuccess/30 bg-xsuccess/10 px-3 py-2 text-sm text-xsuccess">
          {success}
        </div>
      )}

      <form onSubmit={handleApprove} className="mt-6 space-y-4 rounded-2xl border border-xborder bg-xbg-secondary p-5">
        <div>
          <label className="mb-2 block text-sm font-medium text-xtext-primary">User code</label>
          <input
            type="text"
            value={userCode}
            onChange={(event) => setUserCode(event.target.value.toUpperCase())}
            placeholder="ABCD-1234"
            required
            className="w-full rounded border border-xborder bg-xbg-primary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-xtext-primary">Link to existing agent (optional)</label>
          <select
            value={selectedAgentId}
            onChange={(event) => setSelectedAgentId(event.target.value)}
            className="w-full rounded border border-xborder bg-xbg-primary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          >
            <option value="">Create new agent</option>
            {ownedAgents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.display_name} · {agent.model_display_name || agent.agent_type}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-xaccent px-4 py-2 text-sm font-medium text-white hover:bg-xaccent-hover"
        >
          {submitting ? "Approving…" : "Approve"}
        </button>
      </form>
    </div>
  );
}
