// forceGraph.js — Modular Force-Directed Graph Renderer
// ------------------------------------------------------

import { colorByType } from "./color.js";
import { enableZoom } from "./zoom.js";
import { setupInfoPanel } from "./infoPanel.js";

export function renderForceGraph(data, container) {

  // Clear previous graph
  container.innerHTML = "";

  const width = container.clientWidth;
  const height = container.clientHeight;

  const infoPanel = setupInfoPanel();

  // --- SVG wrapper ---
  const svg = d3.select(container)
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .style("background", "#111")
    .style("cursor", "grab");

  const g = svg.append("g").attr("class", "graph-root");

  const gLinks = g.append("g").attr("class", "g-links");
  const gNodes = g.append("g").attr("class", "g-nodes");

  // --- Scales based on usage metrics ---
  const extent = d3.extent(
    data.nodes.map(n => n.decl_count || n.usage_count || 0)
  );

  const sizeScale = d3.scaleSqrt()
    .domain(extent)
    .range([3, 14]);

  const opacityScale = d3.scaleLinear()
    .domain(extent)
    .range([0.3, 1]);

  // --- Enable zoom/pan ---
  enableZoom(svg, g);

  // --- Links ---
  const link = gLinks.selectAll("line")
    .data(data.links)
    .enter()
    .append("line")
    .attr("stroke", d => colorByType(d.type))
    .attr("stroke-opacity", 0.35)
    .attr("stroke-width", d => (d.type === "matches" ? 1.5 : 0.7));

  // --- Drag Behavior ---
  const drag = d3.drag()
    .on("start", (event, d) => {
      if (!event.active) sim.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    })
    .on("drag", (event, d) => {
      d.fx = event.x;
      d.fy = event.y;
    })
    .on("end", (event, d) => {
      if (!event.active) sim.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    });

  // --- Nodes ---
  const node = gNodes.selectAll("circle")
    .data(data.nodes)
    .enter()
    .append("circle")
    .attr("r", d => sizeScale(d.decl_count || d.usage_count || 0))
    .attr("fill", d => colorByType(d.type))
    .attr("opacity", d => opacityScale(d.decl_count || d.usage_count || 0))
    .attr("stroke", "#fff")
    .attr("stroke-width", 0.5)
    .call(drag)
    .on("click", (event, d) => {
      event.stopPropagation();
      infoPanel.show(d);
    });

  // Clicking empty background clears info panel
  svg.on("click", e => {
    if (e.target.tagName === "svg") infoPanel.clear();
  });

  // --- Force Simulation ---
  const sim = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links)
      .id(d => d.id)
      .distance(40)
    )
    .force("charge", d3.forceManyBody().strength(-140))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .alphaDecay(0.05);

  sim.on("tick", () => {
    link.attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node.attr("cx", d => d.x)
        .attr("cy", d => d.y);
  });

  // --- Public API (legend support) ---
  return {
    svg,
    destroy() {
      sim.stop();
      svg.remove();
    },

    toggleType(type, visible) {
      node
        .filter(d => d.type === type)
        .transition()
        .duration(200)
        .style("opacity", visible ? 1 : 0)
        .style("pointer-events", visible ? "all" : "none");

      link
        .transition()
        .duration(200)
        .style("opacity", l => {
          const match = (l.source.type === type || l.target.type === type);
          return match ? (visible ? 0.35 : 0) : 0.35;
        });
    }
  };
}