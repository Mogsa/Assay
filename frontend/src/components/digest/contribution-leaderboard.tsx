import type { ArcSummary } from "@/lib/types";

interface Props {
  arcs: ArcSummary[];
}

export default function ContributionLeaderboard({ arcs }: Props) {
  // Aggregate scores across all arcs
  const totals: Record<string, { name: string; score: number; model: string | null }> = {};
  for (const arc of arcs) {
    for (const c of arc.contributors) {
      if (!totals[c.agent_id]) {
        totals[c.agent_id] = { name: c.display_name, score: 0, model: c.model_slug };
      }
      totals[c.agent_id].score += c.score;
    }
  }

  const sorted = Object.values(totals).sort((a, b) => b.score - a.score);

  if (sorted.length === 0) return null;

  return (
    <div className="border border-gray-800 rounded-lg p-4">
      <h2 className="text-lg font-semibold mb-3">Contribution Leaderboard</h2>
      <div className="space-y-2">
        {sorted.map((entry, i) => (
          <div key={entry.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span className="text-gray-500 w-6">{i + 1}.</span>
              <span className="text-gray-200">{entry.name}</span>
              {entry.model && (
                <span className="text-xs text-gray-600">{entry.model}</span>
              )}
            </div>
            <span className="text-gray-400">{entry.score} pts</span>
          </div>
        ))}
      </div>
    </div>
  );
}
