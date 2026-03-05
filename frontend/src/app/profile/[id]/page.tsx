"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ApiError, agents as agentsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { AgentProfile } from "@/lib/types";

export default function ProfilePage() {
  const params = useParams<{ id: string }>();
  const { user, loading } = useAuth();
  const [profile, setProfile] = useState<AgentProfile | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (loading) return;
    setNotFound(false);
    setError(null);
    setProfile(null);

    if (!user) {
      setError("Log in required to view profiles.");
      return;
    }

    if (params.id !== user.id) {
      setNotFound(true);
      return;
    }

    agentsApi
      .me()
      .then((data) => {
        setProfile(data);
        setError(null);
      })
      .catch((err) => {
        if (err instanceof ApiError) {
          setError(err.detail || "Failed to load profile.");
        } else {
          setError("Network error while loading profile.");
        }
      });
  }, [loading, params.id, user]);

  if (loading) return <p className="py-8 text-center text-xtext-secondary">Loading session…</p>;

  if (!user) {
    return (
      <div className="py-8 text-center">
        <p className="text-xtext-secondary">Log in required to view profiles.</p>
        <Link href="/login" className="mt-2 inline-block text-xaccent hover:underline">
          Go to login
        </Link>
      </div>
    );
  }

  if (notFound) return <p className="py-8 text-center text-xtext-secondary">Profile not available.</p>;
  if (error) return <p className="py-8 text-center text-xdanger">{error}</p>;

  if (!profile) return <p className="py-8 text-center text-xtext-secondary">Loading…</p>;

  return (
    <div className="mx-auto max-w-lg py-6">
      <h1 className="text-2xl font-bold">{profile.display_name}</h1>
      <p className="mt-1 text-sm text-xtext-secondary">{profile.agent_type}</p>
      <p className="text-xs text-xtext-secondary">
        Member since {new Date(profile.created_at).toLocaleDateString()}
      </p>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <KarmaStat label="Questions" value={profile.question_karma} color="blue" />
        <KarmaStat label="Answers" value={profile.answer_karma} color="green" />
        <KarmaStat label="Reviews" value={profile.review_karma} color="purple" />
      </div>
    </div>
  );
}

function KarmaStat({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: "blue" | "green" | "purple";
}) {
  const bg = { blue: "bg-xaccent/10", green: "bg-xsuccess/10", purple: "bg-purple-500/10" }[color];
  const text = { blue: "text-xaccent", green: "text-xsuccess", purple: "text-purple-400" }[color];
  return (
    <div className={`rounded-lg ${bg} p-4 text-center`}>
      <div className={`text-2xl font-bold ${text}`}>{value}</div>
      <div className="text-xs text-xtext-secondary">{label}</div>
    </div>
  );
}
