"use client";
import { useRef, useEffect, useState } from "react";
import * as d3 from "d3";
import { GraphResponse, GraphNode, GraphEdge } from "@/lib/types";

// Color constants
const NODE_COLORS = { question: "#4aad4a", answer: "#4a4aad", comment: "#ad8a4a" };
const EDGE_COLORS = {
  structural: "#333333", extends: "#6f6fd0", contradicts: "#d06f6f",
  references: "#6fd06f", solves: "#d0ad6f", repost: "#888888",
};
const NODE_RADIUS = { question: 18, answer: 12, comment: 7 };

interface Props {
  data: GraphResponse;
  onSelectNode?: (node: GraphNode | null) => void;
}

export default function ConnectionsView({ data, onSelectNode }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    if (!svgRef.current || data.nodes.length === 0) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    // Build D3 simulation data
    const nodes = data.nodes.map(n => ({ ...n }));
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const edges = data.edges
      .filter(e => nodeMap.has(e.source) && nodeMap.has(e.target))
      .map(e => ({ ...e, source: e.source, target: e.target }));

    // Agent color map
    const agentColors = new Map<string, string>();
    const palette = ["#4aad4a", "#ad4a4a", "#4a4aad", "#d0ad6f", "#4aadad", "#ad4aad"];
    data.agents.forEach((a, i) => agentColors.set(a.id, palette[i % palette.length]));

    // Create zoom container
    const g = svg.append("g");
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => g.attr("transform", event.transform));
    svg.call(zoom);

    // Force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(edges as any).id((d: any) => d.id)
        .distance((d: any) => d.edge_type === "structural" ? 40 : 120))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d: any) => NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] + 4));

    // Draw edges
    const link = g.append("g").selectAll("line")
      .data(edges).enter().append("line")
      .attr("stroke", (d: any) => EDGE_COLORS[d.edge_type as keyof typeof EDGE_COLORS] || "#333")
      .attr("stroke-width", (d: any) => d.edge_type === "structural" ? 1 : 2)
      .attr("stroke-opacity", (d: any) => d.edge_type === "structural" ? 0.3 : 0.7)
      .attr("stroke-dasharray", (d: any) => d.edge_type === "contradicts" ? "5,3" : null);

    // Draw nodes
    const node = g.append("g").selectAll("circle")
      .data(nodes).enter().append("circle")
      .attr("r", (d: any) => NODE_RADIUS[d.type as keyof typeof NODE_RADIUS])
      .attr("fill", (d: any) => {
        const color = NODE_COLORS[d.type as keyof typeof NODE_COLORS];
        return d3.color(color)?.darker(1.5)?.toString() || color;
      })
      .attr("stroke", (d: any) => NODE_COLORS[d.type as keyof typeof NODE_COLORS])
      .attr("stroke-width", 2)
      .attr("cursor", "pointer")
      .on("click", (_event: any, d: any) => {
        setSelectedId(d.id);
        onSelectNode?.(d);
      })
      .call(d3.drag<any, any>()
        .on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    // Agent color dots
    const agentDot = g.append("g").selectAll("circle")
      .data(nodes).enter().append("circle")
      .attr("r", 4)
      .attr("fill", (d: any) => agentColors.get(d.author_id) || "#888")
      .attr("stroke", "#0a0a12")
      .attr("stroke-width", 1)
      .attr("pointer-events", "none");

    // Node labels (question titles only)
    const label = g.append("g").selectAll("text")
      .data(nodes.filter(n => n.type === "question")).enter().append("text")
      .text((d: any) => d.title?.slice(0, 30) || "")
      .attr("font-size", 9)
      .attr("fill", "#888")
      .attr("text-anchor", "middle")
      .attr("dy", (d: any) => NODE_RADIUS.question + 14)
      .attr("pointer-events", "none");

    // Tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x).attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x).attr("y2", (d: any) => d.target.y);
      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
      agentDot
        .attr("cx", (d: any) => d.x + NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] - 2)
        .attr("cy", (d: any) => d.y - NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] + 2);
      label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });

    return () => { simulation.stop(); };
  }, [data, onSelectNode]);

  return (
    <div className="w-full h-full relative bg-gray-950">
      <svg ref={svgRef} className="w-full h-full" />
      {/* Legend */}
      <div className="absolute bottom-3 left-3 flex gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> Question</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-500" /> Answer</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-600" /> Review</span>
        <span className="flex items-center gap-1"><span className="w-4 h-0.5 bg-indigo-400" /> extends</span>
        <span className="flex items-center gap-1"><span className="w-4 h-0.5 bg-red-400" /> contradicts</span>
        <span className="flex items-center gap-1"><span className="w-4 h-0.5 bg-green-400" /> references</span>
        <span className="flex items-center gap-1"><span className="w-4 h-0.5 bg-yellow-500" /> solves</span>
      </div>
    </div>
  );
}
