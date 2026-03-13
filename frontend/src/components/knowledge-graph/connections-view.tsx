"use client";
import { GraphResponse } from "@/lib/types";

export default function ConnectionsView({ data }: { data: GraphResponse }) {
  return <div className="p-8 text-gray-500">Connections view — {data.nodes.length} nodes, {data.edges.length} edges</div>;
}
