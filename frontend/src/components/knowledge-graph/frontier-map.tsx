"use client";
import { useRef, useEffect } from "react";
import * as d3 from "d3";
import { GraphResponse, FrontierResponse } from "@/lib/types";

type Zone = "explored" | "frontier" | "debated" | "isolated";

const ZONE_COLORS: Record<Zone, string> = {
  explored: "#4aad4a",
  frontier: "#6f6fd0",
  debated: "#d06f6f",
  isolated: "#555555",
};

export default function FrontierMap({ data, frontier }: { data: GraphResponse; frontier: FrontierResponse }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;
    const cx = width / 2;
    const cy = height / 2;

    // Build classification sets
    const frontierIds = new Set(frontier.frontier_questions.map(q => q.id));
    const debateIds = new Set(frontier.active_debates.map(d => d.question_id));
    const isolatedIds = new Set(frontier.isolated_questions.map(q => q.id));

    // Classify question nodes
    const questionNodes = data.nodes.filter(n => n.type === "question");
    const classified = questionNodes.map(n => {
      let zone: Zone = "explored";
      if (frontierIds.has(n.id)) zone = "frontier";
      else if (debateIds.has(n.id)) zone = "debated";
      else if (isolatedIds.has(n.id)) zone = "isolated";
      return { ...n, zone };
    });

    // Group by zone
    const groups: Record<Zone, typeof classified> = {
      explored: classified.filter(n => n.zone === "explored"),
      frontier: classified.filter(n => n.zone === "frontier"),
      debated: classified.filter(n => n.zone === "debated"),
      isolated: classified.filter(n => n.zone === "isolated"),
    };

    // Position nodes in concentric rings
    const maxRadius = Math.min(width, height) / 2 - 60;
    const zoneRadii: Record<Zone, number> = {
      explored: maxRadius * 0.2,
      frontier: maxRadius * 0.55,
      debated: maxRadius * 0.55,
      isolated: maxRadius * 0.85,
    };

    type PositionedNode = (typeof classified)[number] & { x: number; y: number };
    const positioned: PositionedNode[] = [];

    // Place nodes in circular arrangement within each zone
    for (const [zone, nodes] of Object.entries(groups) as [Zone, typeof classified][]) {
      const r = zoneRadii[zone];
      const angleOffset = zone === "debated" ? Math.PI : 0; // debated on opposite side from frontier
      nodes.forEach((n, i) => {
        const count = nodes.length;
        const angle = count === 1
          ? angleOffset
          : angleOffset + (2 * Math.PI * i) / count;
        const jitter = r * 0.15;
        const nr = r + (Math.random() - 0.5) * jitter;
        positioned.push({
          ...n,
          x: cx + nr * Math.cos(angle),
          y: cy + nr * Math.sin(angle),
        });
      });
    }

    // Zoom container
    const g = svg.append("g");
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on("zoom", (event) => g.attr("transform", event.transform));
    svg.call(zoom);

    // Glow filter definition
    const defs = svg.append("defs");
    const filter = defs.append("filter").attr("id", "glow");
    filter.append("feGaussianBlur").attr("stdDeviation", "3").attr("result", "coloredBlur");
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Decorative zone rings
    const ringData = [
      { r: zoneRadii.explored + 30, opacity: 0.3 },
      { r: zoneRadii.frontier + 30, opacity: 0.24 },
      { r: zoneRadii.isolated + 30, opacity: 0.15 },
    ];
    ringData.forEach(ring => {
      g.append("circle")
        .attr("cx", cx).attr("cy", cy)
        .attr("r", ring.r)
        .attr("fill", "none")
        .attr("stroke", "#444")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4,4")
        .attr("opacity", ring.opacity);
    });

    // Red highlight behind debate nodes
    const debateNodes = positioned.filter(n => n.zone === "debated");
    debateNodes.forEach(n => {
      g.insert("circle", ":first-child")
        .attr("cx", n.x).attr("cy", n.y)
        .attr("r", 24)
        .attr("fill", ZONE_COLORS.debated)
        .attr("opacity", 0.15);
    });

    // Draw nodes
    g.append("g").selectAll("circle")
      .data(positioned).enter().append("circle")
      .attr("cx", d => d.x)
      .attr("cy", d => d.y)
      .attr("r", 14)
      .attr("fill", d => {
        const color = ZONE_COLORS[d.zone];
        return d3.color(color)?.darker(1.2)?.toString() || color;
      })
      .attr("stroke", d => ZONE_COLORS[d.zone])
      .attr("stroke-width", 2)
      .attr("opacity", d => d.zone === "isolated" ? 0.4 : 1)
      .attr("filter", d => d.zone === "frontier" ? "url(#glow)" : null)
      .attr("cursor", "pointer");

    // Pulsing rings for frontier nodes
    const frontierNodes = positioned.filter(n => n.zone === "frontier");
    frontierNodes.forEach(n => {
      g.append("circle")
        .attr("cx", n.x).attr("cy", n.y)
        .attr("r", 14)
        .attr("fill", "none")
        .attr("stroke", ZONE_COLORS.frontier)
        .attr("stroke-width", 1.5)
        .attr("opacity", 0.6)
        .append("animate")
        .attr("attributeName", "r")
        .attr("from", "14").attr("to", "28")
        .attr("dur", "2s")
        .attr("repeatCount", "indefinite");

      g.append("circle")
        .attr("cx", n.x).attr("cy", n.y)
        .attr("r", 14)
        .attr("fill", "none")
        .attr("stroke", ZONE_COLORS.frontier)
        .attr("stroke-width", 1.5)
        .append("animate")
        .attr("attributeName", "opacity")
        .attr("from", "0.6").attr("to", "0")
        .attr("dur", "2s")
        .attr("repeatCount", "indefinite");
    });

    // Node labels
    g.append("g").selectAll("text")
      .data(positioned).enter().append("text")
      .text(d => d.title?.slice(0, 25) || "")
      .attr("x", d => d.x)
      .attr("y", d => d.y + 24)
      .attr("font-size", 9)
      .attr("fill", d => d.zone === "isolated" ? "#555" : "#888")
      .attr("text-anchor", "middle")
      .attr("pointer-events", "none");

    return () => {};
  }, [data, frontier]);

  return (
    <div className="w-full h-full relative bg-gray-950">
      <svg ref={svgRef} className="w-full h-full" />
      {/* Legend */}
      <div className="absolute bottom-3 left-3 flex gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full" style={{ background: ZONE_COLORS.explored }} />
          Explored
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full" style={{ background: ZONE_COLORS.frontier }} />
          Frontier
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full" style={{ background: ZONE_COLORS.debated }} />
          Debated
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full opacity-40" style={{ background: ZONE_COLORS.isolated }} />
          Isolated
        </span>
      </div>
    </div>
  );
}
