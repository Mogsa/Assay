"use client";
import { GraphResponse, FrontierResponse } from "@/lib/types";

export default function FrontierMap({ data, frontier }: { data: GraphResponse; frontier: FrontierResponse }) {
  return (
    <div className="p-8 text-gray-500">
      Frontier map — {frontier.frontier_questions.length} frontier, {frontier.active_debates.length} debates, {frontier.isolated_questions.length} isolated
    </div>
  );
}
