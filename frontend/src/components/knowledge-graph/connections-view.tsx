"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useRef, useEffect } from "react";
import * as d3 from "d3";
import { GraphNode, GraphResponse, FrontierResponse, GraphFilterState, FrontierStatus } from "@/lib/types";

// --- Classification helper (named export for page component) ---

export function classifyNode(
  node: GraphNode,
  frontierIds: Set<string>,
  debateIds: Set<string>,
  isolatedIds: Set<string>,
): FrontierStatus {
  if (frontierIds.has(node.id)) return "frontier";
  if (debateIds.has(node.id)) return "debated";
  if (isolatedIds.has(node.id)) return "isolated";
  if (node.status === "resolved") return "resolved";
  return "explored";
}

// --- Constants ---

const STATUS_COLORS: Record<FrontierStatus, { fill: string; stroke: string }> = {
  frontier: { fill: "#1a1a3a", stroke: "#6f6fd0" },
  debated:  { fill: "#3a1a1a", stroke: "#d06f6f" },
  resolved: { fill: "#1a3a1a", stroke: "#4aad4a" },
  explored: { fill: "#1a1a1a", stroke: "#555555" },
  isolated: { fill: "#111111", stroke: "#333333" },
};

const EDGE_COLORS: Record<string, string> = {
  extends: "#6f6fd0", contradicts: "#d06f6f", references: "#6fd06f",
  structural: "#333333",
};

const NODE_RADIUS = { question: 18, answer: 12, comment: 7 };
const AGENT_PALETTE = ["#4aad4a", "#ad4a4a", "#4a4aad", "#d0ad6f", "#4aadad", "#ad4aad"];

// --- Link type filter key mapping ---

const LINK_FILTER_MAP: Record<string, keyof GraphFilterState> = {
  extends: "showExtends",
  contradicts: "showContradicts",
  references: "showReferences",
};

// --- Status filter key mapping ---

const STATUS_FILTER_MAP: Record<FrontierStatus, keyof GraphFilterState> = {
  frontier: "showFrontier",
  debated: "showDebated",
  resolved: "showResolved",
  explored: "showExplored",
  isolated: "showIsolated",
};

interface Props {
  data: GraphResponse;
  frontier: FrontierResponse | null;
  filters: GraphFilterState;
  onSelectNode: (node: GraphNode | null) => void;
  onSelectCommunity: (communityId: string) => void;
}

export default function ConnectionsView({ data, frontier, filters, onSelectNode, onSelectCommunity }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || data.nodes.length === 0) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    // Remove any old tooltips
    d3.select(containerRef.current).selectAll(".graph-tooltip").remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    // Build classification sets from frontier data
    const frontierIds = new Set(frontier?.frontier_questions.map(q => q.id) ?? []);
    const debateIds = new Set(frontier?.active_debates.map(d => d.question_id) ?? []);
    const isolatedIds = new Set(frontier?.isolated_questions.map(q => q.id) ?? []);

    const classify = (node: GraphNode): FrontierStatus =>
      classifyNode(node, frontierIds, debateIds, isolatedIds);

    // Agent color map
    const agentColors = new Map<string, string>();
    data.agents.forEach((a, i) => agentColors.set(a.id, AGENT_PALETTE[i % AGENT_PALETTE.length]));

    const isDrillDown = filters.view === "community" && !!filters.selectedCommunityId;

    // --- Filter nodes ---
    let filteredNodes: GraphNode[];
    if (isDrillDown) {
      // Drill-down: all nodes for selected community
      const communityQuestionIds = new Set(
        data.nodes
          .filter(n => n.type === "question" && (
            filters.selectedCommunityId === "__uncategorized__"
              ? !n.community_id
              : n.community_id === filters.selectedCommunityId
          ))
          .map(n => n.id)
      );
      const communityAnswerIds = new Set(
        data.nodes
          .filter(n => n.type === "answer" && n.question_id && communityQuestionIds.has(n.question_id))
          .map(n => n.id)
      );
      filteredNodes = data.nodes.filter(n =>
        communityQuestionIds.has(n.id) ||
        communityAnswerIds.has(n.id) ||
        (n.type === "comment" && n.answer_id && communityAnswerIds.has(n.answer_id))
      );
    } else {
      // Overview: questions only, filtered by status
      filteredNodes = data.nodes.filter(n => {
        if (n.type !== "question") return false;
        const status = classify(n);
        const filterKey = STATUS_FILTER_MAP[status];
        return filters[filterKey] as boolean;
      });
    }

    if (filteredNodes.length === 0) return;

    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));

    // --- Filter edges ---
    const filteredEdges = data.edges.filter(e => {
      const srcId = typeof e.source === "object" ? (e.source as any).id : e.source;
      const tgtId = typeof e.target === "object" ? (e.target as any).id : e.target;
      if (!filteredNodeIds.has(srcId) || !filteredNodeIds.has(tgtId)) return false;

      if (isDrillDown) {
        // Show all edge types in drill-down
        if (e.edge_type === "structural") return true;
        const filterKey = LINK_FILTER_MAP[e.edge_type];
        return filterKey ? (filters[filterKey] as boolean) : true;
      } else {
        // Overview: semantic only, filtered by link type
        if (e.edge_type === "structural") return false;
        const filterKey = LINK_FILTER_MAP[e.edge_type];
        return filterKey ? (filters[filterKey] as boolean) : true;
      }
    });

    // Cross-community edges for drill-down
    const crossCommunityEdges = isDrillDown ? data.edges.filter(e => {
      if (e.edge_type === "structural") return false;
      const srcId = typeof e.source === "object" ? (e.source as any).id : e.source;
      const tgtId = typeof e.target === "object" ? (e.target as any).id : e.target;
      const srcIn = filteredNodeIds.has(srcId);
      const tgtIn = filteredNodeIds.has(tgtId);
      return (srcIn && !tgtIn) || (!srcIn && tgtIn);
    }) : [];

    // --- Build D3 simulation data ---
    const nodes = filteredNodes.map(n => ({
      ...n,
      _status: classify(n),
    }));
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const edges = filteredEdges.map(e => ({ ...e, source: e.source as string, target: e.target as string }));

    // Create zoom container
    const g = svg.append("g");
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => g.attr("transform", event.transform));
    svg.call(zoom);

    // --- Force simulation ---
    let simulation: d3.Simulation<any, any>;
    const commIds = Array.from(new Set(filteredNodes.map(n => n.community_id || "__uncategorized__")));

    if (isDrillDown) {
      // Single community — standard layout
      simulation = d3.forceSimulation(nodes as any)
        .force("link", d3.forceLink(edges as any).id((d: any) => d.id)
          .distance((d: any) => d.edge_type === "structural" ? 40 : 120))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius((d: any) =>
          NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] + 4));
    } else {
      // Overview — community gravity wells
      const communityPositions = new Map<string, { x: number; y: number }>();
      commIds.forEach((cid, i) => {
        const angle = (2 * Math.PI * i) / commIds.length;
        const radius = Math.min(width, height) * 0.38;
        communityPositions.set(cid, {
          x: width / 2 + radius * Math.cos(angle),
          y: height / 2 + radius * Math.sin(angle),
        });
      });

      // Draw community halos
      const haloGroup = g.append("g").attr("class", "halos");
      commIds.forEach(cid => {
        const pos = communityPositions.get(cid)!;
        const count = filteredNodes.filter(n => (n.community_id || "__uncategorized__") === cid).length;
        const haloRadius = Math.max(80, Math.sqrt(count) * 50);
        const community = data.communities.find(c => c.id === cid);

        haloGroup.append("ellipse")
          .attr("class", `halo-ellipse-${cid.replace(/[^a-zA-Z0-9]/g, "")}`)
          .attr("cx", pos.x).attr("cy", pos.y)
          .attr("rx", haloRadius).attr("ry", haloRadius * 0.8)
          .attr("fill", "rgba(255,255,255,0.02)")
          .attr("stroke", "rgba(255,255,255,0.06)")
          .attr("stroke-width", 1)
          .attr("cursor", "pointer")
          .on("click", () => onSelectCommunity(cid));

        haloGroup.append("text")
          .attr("class", `halo-label-${cid.replace(/[^a-zA-Z0-9]/g, "")}`)
          .attr("x", pos.x).attr("y", pos.y - haloRadius * 0.8 - 8)
          .attr("text-anchor", "middle")
          .attr("fill", "#555")
          .attr("font-size", 11)
          .attr("cursor", "pointer")
          .text(community?.name || "Uncategorized")
          .on("click", () => onSelectCommunity(cid));
      });

      // Build a set of cross-community edges for weaker link strength
      const crossEdges = new Set<number>();
      edges.forEach((e: any, i: number) => {
        const src = nodeMap.get(e.source);
        const tgt = nodeMap.get(e.target);
        if (src && tgt && src.community_id !== tgt.community_id) {
          crossEdges.add(i);
        }
      });

      simulation = d3.forceSimulation(nodes as any)
        .force("link", d3.forceLink(edges as any).id((d: any) => d.id)
          .distance((_: any, i: number) => crossEdges.has(i) ? 300 : 80)
          .strength((_: any, i: number) => crossEdges.has(i) ? 0.03 : 0.3))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("x", d3.forceX((d: any) => {
          const center = communityPositions.get(d.community_id || "__uncategorized__");
          return center?.x ?? width / 2;
        }).strength(0.6))
        .force("y", d3.forceY((d: any) => {
          const center = communityPositions.get(d.community_id || "__uncategorized__");
          return center?.y ?? height / 2;
        }).strength(0.6))
        .force("collision", d3.forceCollide().radius(22));
    }

    // Detect cross-community edges BEFORE forceLink mutates source/target to objects
    const crossEdgeIds = new Set<string>();
    if (!isDrillDown) {
      for (const e of edges) {
        const srcId = typeof e.source === "object" ? (e.source as any).id : e.source;
        const tgtId = typeof e.target === "object" ? (e.target as any).id : e.target;
        const src = nodeMap.get(srcId);
        const tgt = nodeMap.get(tgtId);
        if (src && tgt && src.community_id !== tgt.community_id) {
          crossEdgeIds.add(`${srcId}-${tgtId}`);
        }
      }
    }

    // Tag each edge with _isCross before D3 mutates them
    edges.forEach((e: any) => {
      const srcId = typeof e.source === "object" ? e.source.id : e.source;
      const tgtId = typeof e.target === "object" ? e.target.id : e.target;
      e._isCross = crossEdgeIds.has(`${srcId}-${tgtId}`);
    });

    // --- Draw edges ---
    const linkGroup = g.append("g");

    // Intra-community links: straight lines
    const intraEdges = edges.filter((d: any) => !d._isCross);
    const intraLink = linkGroup.selectAll("line.intra")
      .data(intraEdges).enter().append("line")
      .attr("class", "intra")
      .attr("stroke", (d: any) => EDGE_COLORS[d.edge_type] || "#333")
      .attr("stroke-width", (d: any) => isDrillDown && d.edge_type === "structural" ? 1.5 : 1.5)
      .attr("stroke-opacity", (d: any) => isDrillDown && d.edge_type === "structural" ? 0.4 : 0.5)
      .attr("stroke-dasharray", (d: any) => d.edge_type === "contradicts" ? "5,3" : null);

    // Cross-community links: curved paths, subtle
    const crossEdgeData = edges.filter((d: any) => d._isCross);
    const crossLink = linkGroup.selectAll("path.cross")
      .data(crossEdgeData).enter().append("path")
      .attr("class", "cross")
      .attr("fill", "none")
      .attr("stroke", (d: any) => EDGE_COLORS[d.edge_type] || "#333")
      .attr("stroke-width", 1)
      .attr("stroke-opacity", 0.25)
      .attr("stroke-dasharray", (d: any) => d.edge_type === "contradicts" ? "5,3" : "6,4");

    // --- Draw nodes ---
    const nodeRadius = (d: any) => isDrillDown
      ? NODE_RADIUS[d.type as keyof typeof NODE_RADIUS]
      : NODE_RADIUS.question;

    const nodeFill = (d: any) => {
      if (d.type === "question" || !isDrillDown) {
        return STATUS_COLORS[d._status as FrontierStatus]?.fill || "#1a1a1a";
      }
      if (d.type === "answer") return "#1a1a2a";
      return "#2a2a1a"; // comment
    };

    const nodeStroke = (d: any) => {
      if (d.type === "question" || !isDrillDown) {
        return STATUS_COLORS[d._status as FrontierStatus]?.stroke || "#555";
      }
      if (d.type === "answer") return "#4a4aad";
      return "#ad8a4a"; // comment
    };

    const node = g.append("g").selectAll("circle")
      .data(nodes).enter().append("circle")
      .attr("r", nodeRadius)
      .attr("fill", nodeFill)
      .attr("stroke", nodeStroke)
      .attr("stroke-width", 2)
      .attr("cursor", "pointer")
      .on("click", (_event: any, d: any) => onSelectNode(d))
      .call(d3.drag<any, any>()
        .on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    // Pulsing ring for frontier nodes
    if (!isDrillDown) {
      const frontierNodes = nodes.filter(n => n._status === "frontier");
      if (frontierNodes.length > 0) {
        // Add CSS animation via a <style> element
        svg.append("defs").append("style").text(`
          @keyframes pulse-ring { 0% { r: 20; opacity: 0.6; } 100% { r: 28; opacity: 0; } }
          .pulse-ring { animation: pulse-ring 2s ease-out infinite; }
        `);
        g.append("g").selectAll("circle")
          .data(frontierNodes).enter().append("circle")
          .attr("class", "pulse-ring")
          .attr("fill", "none")
          .attr("stroke", STATUS_COLORS.frontier.stroke)
          .attr("stroke-width", 1.5)
          .attr("pointer-events", "none");
      }
    }

    // Agent color dots (drill-down only, on answers/comments)
    let agentDot: d3.Selection<any, any, any, any> | null = null;
    if (isDrillDown) {
      const agentDotNodes = nodes.filter(n => n.type !== "question");
      agentDot = g.append("g").selectAll("circle")
        .data(agentDotNodes).enter().append("circle")
        .attr("r", 4)
        .attr("fill", (d: any) => agentColors.get(d.author_id) || "#888")
        .attr("stroke", "#0a0a12")
        .attr("stroke-width", 1)
        .attr("pointer-events", "none");
    }

    // Answer count badges (overview only)
    let answerBadge: d3.Selection<any, any, any, any> | null = null;
    if (!isDrillDown) {
      const questionsWithAnswers = nodes.filter(n => n.answer_count && n.answer_count > 0);
      answerBadge = g.append("g").selectAll("text")
        .data(questionsWithAnswers).enter().append("text")
        .text((d: any) => d.answer_count)
        .attr("font-size", 8)
        .attr("fill", "#aaa")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("pointer-events", "none");
    }

    // Verdict badges (drill-down, comment nodes)
    let verdictLabel: d3.Selection<any, any, any, any> | null = null;
    if (isDrillDown) {
      const verdictNodes = nodes.filter(n => n.type === "comment" && n.verdict);
      const verdictSymbol: Record<string, { symbol: string; color: string }> = {
        correct: { symbol: "\u2713", color: "#4aad4a" },
        incorrect: { symbol: "\u2717", color: "#d06f6f" },
        unsure: { symbol: "~", color: "#d0ad6f" },
        partially_correct: { symbol: "?", color: "#d0d04a" },
      };
      verdictLabel = g.append("g").selectAll("text")
        .data(verdictNodes).enter().append("text")
        .text((d: any) => {
          const v = verdictSymbol[d.verdict] || { symbol: "?" };
          return `${v.symbol} ${d.verdict}`;
        })
        .attr("font-size", 8)
        .attr("fill", (d: any) => verdictSymbol[d.verdict]?.color || "#888")
        .attr("text-anchor", "middle")
        .attr("pointer-events", "none");
    }

    // Node labels (question titles)
    const questionNodes = nodes.filter(n => n.type === "question");
    const label = g.append("g").selectAll("text")
      .data(questionNodes).enter().append("text")
      .text((d: any) => d.title?.slice(0, 30) || "")
      .attr("font-size", 9)
      .attr("fill", "#888")
      .attr("text-anchor", "middle")
      .attr("dy", (NODE_RADIUS.question + 14))
      .attr("pointer-events", "none");

    // Cross-community edge indicators (drill-down only)
    let crossLabels: d3.Selection<any, any, any, any> | null = null;
    if (isDrillDown && crossCommunityEdges.length > 0) {
      const crossData = crossCommunityEdges.map(e => {
        const srcId = typeof e.source === "object" ? (e.source as any).id : e.source;
        const tgtId = typeof e.target === "object" ? (e.target as any).id : e.target;
        const localId = filteredNodeIds.has(srcId) ? srcId : tgtId;
        const remoteId = filteredNodeIds.has(srcId) ? tgtId : srcId;
        const remoteNode = data.nodes.find(n => n.id === remoteId);
        const remoteCommunity = remoteNode?.community_id
          ? data.communities.find(c => c.id === remoteNode.community_id)?.name || "other"
          : "Uncategorized";
        return { localId, remoteCommunity, edgeType: e.edge_type };
      });

      crossLabels = g.append("g").selectAll("text")
        .data(crossData).enter().append("text")
        .text((d: any) => `\u2192 ${d.remoteCommunity}`)
        .attr("font-size", 8)
        .attr("fill", (d: any) => EDGE_COLORS[d.edgeType] || "#555")
        .attr("text-anchor", "start")
        .attr("pointer-events", "none");
    }

    // --- Tooltip ---
    const tooltip = d3.select(containerRef.current)
      .append("div")
      .attr("class", "graph-tooltip absolute pointer-events-none bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs hidden z-50")
      .style("max-width", "200px");

    node.on("mouseover", (event: any, d: any) => {
      const statusColor = STATUS_COLORS[d._status as FrontierStatus]?.stroke || "#555";
      tooltip
        .classed("hidden", false)
        .html(`
          <div class="font-semibold text-gray-200 mb-1">${d.title?.slice(0, 60) || d.body_preview?.slice(0, 60) || "Untitled"}</div>
          <div class="text-gray-400">Status: <span style="color:${statusColor}">${d._status}</span></div>
          ${d.answer_count != null ? `<div class="text-gray-400">Answers: ${d.answer_count} &middot; Frontier: ${d.frontier_score.toFixed(1)}</div>` : `<div class="text-gray-400">Frontier: ${d.frontier_score.toFixed(1)}</div>`}
        `)
        .style("left", `${event.offsetX + 15}px`)
        .style("top", `${event.offsetY - 10}px`);
    })
    .on("mousemove", (event: any) => {
      tooltip
        .style("left", `${event.offsetX + 15}px`)
        .style("top", `${event.offsetY - 10}px`);
    })
    .on("mouseout", () => tooltip.classed("hidden", true));

    // Pulsing rings selection
    const pulseRings = g.selectAll(".pulse-ring");

    // --- Tick ---
    simulation.on("tick", () => {
      // Straight intra-community links
      intraLink
        .attr("x1", (d: any) => d.source.x).attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x).attr("y2", (d: any) => d.target.y);

      // Curved cross-community links
      crossLink.attr("d", (d: any) => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 0.8;
        return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
      });

      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);

      if (agentDot) {
        agentDot
          .attr("cx", (d: any) => d.x + NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] - 2)
          .attr("cy", (d: any) => d.y - NODE_RADIUS[d.type as keyof typeof NODE_RADIUS] + 2);
      }

      if (answerBadge) {
        answerBadge.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
      }

      pulseRings.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);

      if (verdictLabel) {
        verdictLabel
          .attr("x", (d: any) => d.x)
          .attr("y", (d: any) => d.y + NODE_RADIUS.comment + 12);
      }

      label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);

      // Update community halos to track node centroids
      if (!isDrillDown) {
        commIds.forEach(cid => {
          const members = (nodes as any[]).filter(
            (n: any) => (n.community_id || "__uncategorized__") === cid
          );
          if (members.length === 0) return;
          const cx = members.reduce((s: number, n: any) => s + n.x, 0) / members.length;
          const cy = members.reduce((s: number, n: any) => s + n.y, 0) / members.length;
          const maxDist = Math.max(
            ...members.map((n: any) => Math.sqrt((n.x - cx) ** 2 + (n.y - cy) ** 2))
          );
          const r = maxDist + 40;
          const safeClass = cid.replace(/[^a-zA-Z0-9]/g, "");
          g.select(`.halo-ellipse-${safeClass}`)
            .attr("cx", cx).attr("cy", cy)
            .attr("rx", r).attr("ry", r * 0.85);
          g.select(`.halo-label-${safeClass}`)
            .attr("x", cx).attr("y", cy - r * 0.85 - 8);
        });
      }

      if (crossLabels) {
        crossLabels.attr("x", (d: any) => {
          const localNode = nodeMap.get(d.localId);
          return localNode ? (localNode as any).x + 24 : 0;
        }).attr("y", (d: any) => {
          const localNode = nodeMap.get(d.localId);
          return localNode ? (localNode as any).y : 0;
        });
      }
    });

    const container = containerRef.current;
    return () => {
      simulation.stop();
      d3.select(container).selectAll(".graph-tooltip").remove();
    };
  }, [data, frontier, filters, onSelectNode, onSelectCommunity]);

  return (
    <div ref={containerRef} className="w-full h-full relative bg-gray-950">
      {/* Breadcrumb for drill-down */}
      {filters.view === "community" && (
        <div className="absolute top-3 left-3 z-10 flex items-center gap-2 text-sm">
          <button
            onClick={() => onSelectCommunity("")}
            className="text-blue-400 hover:text-blue-300"
          >
            ← All Communities
          </button>
          <span className="text-gray-600">/</span>
          <span className="text-gray-300">
            {data.communities.find(c => c.id === filters.selectedCommunityId)?.name || "Uncategorized"}
          </span>
        </div>
      )}
      <svg ref={svgRef} className="w-full h-full" />
      {/* Legend */}
      {filters.view === "overview" && (
        <div className="absolute bottom-3 left-3 flex gap-4 text-xs text-gray-500">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{background: STATUS_COLORS.frontier.stroke}} /> Frontier</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{background: STATUS_COLORS.debated.stroke}} /> Debated</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{background: STATUS_COLORS.resolved.stroke}} /> Resolved</span>
          <span className="flex items-center gap-1"><span className="w-4 h-0.5" style={{background: EDGE_COLORS.extends}} /> extends</span>
          <span className="flex items-center gap-1"><span className="w-4 h-0.5" style={{background: EDGE_COLORS.contradicts}} /> contradicts</span>
          <span className="flex items-center gap-1"><span className="w-4 h-0.5" style={{background: EDGE_COLORS.references}} /> references</span>
        </div>
      )}
    </div>
  );
}
