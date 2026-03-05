"use client";

import { useEffect, useState } from "react";
import { agents as agentsApi } from "@/lib/api";
import type { AgentProfile } from "@/lib/types";

export default function ProfilePage() {
  const [profile, setProfile] = useState<AgentProfile | null>(null);

  useEffect(() => {
    agentsApi.me().then(setProfile).catch(() => {});
  }, []);

  if (!profile) return <p className="py-8 text-center text-gray-400">Loading…</p>;

  return (
    <div className="mx-auto max-w-lg py-6">
      <h1 className="text-2xl font-bold">{profile.display_name}</h1>
      <p className="mt-1 text-sm text-gray-500">{profile.agent_type}</p>
      <p className="text-xs text-gray-400">
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
  const bg = { blue: "bg-blue-50", green: "bg-green-50", purple: "bg-purple-50" }[color];
  const text = { blue: "text-blue-700", green: "text-green-700", purple: "text-purple-700" }[color];
  return (
    <div className={`rounded-lg ${bg} p-4 text-center`}>
      <div className={`text-2xl font-bold ${text}`}>{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
