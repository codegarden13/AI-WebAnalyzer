// graph.js — D3 force graph with zoom + tooltip integration
import { colorByType } from './color.js';
import { setupTooltip } from './tooltip.js';

export function renderGraph(data, container, onNodeClick) {
  const width = window.innerWidth;
  const height = window.innerHeight;

  // === SVG + zoom container ===
  const svg = container.append("svg")
    .attr("width", width)
    .attr("height", height)
    .style("background", "#111");

  const g = svg.append("g");

  const zoom = d3.zoom()
    .scaleExtent([0.25, 6])
    .on("zoom", (event) => g.attr("transform", event.transform));

  svg.call(zoom).on("dblclick.zoom", null);

  // === Links ===
  const link = g.append("g")
    .attr("stroke-opacity", 0.4)
    .selectAll("line")
    .data(data.links)
    .enter()
    .append("line")
    .attr("stroke", d => colorByType(d.type))
    .attr("stroke-width", d => (d.type === "matches" ? 1.5 : 0.8))
    .attr("stroke-dasharray", d => (d.type === "matches" ? "4,2" : "0"));

  // === Nodes ===
  const node = g.append("g")
    .selectAll("circle")
    .data(data.nodes)
    .enter()
    .append("circle")
    .attr("r", 4)
    .attr("fill", d => colorByType(d.type))
    .attr("stroke", "#fff")
    .attr("stroke-width", 0.5)
    .attr("opacity", 0.9)
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended))
    .on("click", (event, d) => {
      if (onNodeClick) onNodeClick(d);
      event.stopPropagation();
    });

  // === Tooltip setup ===
  const tooltip = setupTooltip();

  node
    .on("mouseover", (event, d) => {
      tooltip.show(event, d);

      // Highlight connected links
      link
        .attr("stroke-opacity", l =>
          l.source.id === d.id || l.target.id === d.id ? 1 : 0.05)
        .attr("stroke-width", l =>
          l.source.id === d.id || l.target.id === d.id ? 2.5 : 0.5);
    })
    .on("mousemove", (event) => tooltip.move(event))
    .on("mouseout", () => {
      tooltip.hide();
      link
        .attr("stroke-opacity", 0.4)
        .attr("stroke-width", d => (d.type === "matches" ? 1.5 : 0.8));
    });

  // === Force Simulation ===
  const sim = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(40))
    .force("charge", d3.forceManyBody().strength(-120))
    .force("center", d3.forceCenter(width / 2, height / 2));

  sim.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
  });

  // === Zoom reset (press "0") ===
  window.addEventListener("keydown", e => {
    if (e.key === "0") {
      svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
    }
  });

  // === Dragging ===
  function dragstarted(event, d) {
    if (!event.active) sim.alphaTarget(0.3).restart();
    d.fx = d.x; d.fy = d.y;
  }
  function dragged(event, d) {
    d.fx = event.x; d.fy = event.y;
  }
  function dragended(event, d) {
    if (!event.active) sim.alphaTarget(0);
    d.fx = null; d.fy = null;
  }

  return { svg, node, link, tooltip, zoom };
}