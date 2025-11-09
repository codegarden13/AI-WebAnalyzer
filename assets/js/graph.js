// graph.js — D3 force graph with zoom + tooltip integration
import { colorByType } from './color.js';
import { setupTooltip } from './tooltip.js';

export function renderGraph(data, container, onNodeClick) {
  const width = window.innerWidth;
  const height = window.innerHeight;

  // === SVG + Zoom Container ===
  const svg = container.append("svg")
    .attr("width", width)
    .attr("height", height)
    .style("background", "#111");

  const g = svg.append("g");
  const tooltip = setupTooltip();
  let selectedNode = null;

  const zoom = d3.zoom()
    .scaleExtent([0.25, 6])
    .on("zoom", (event) => g.attr("transform", event.transform));
  svg.call(zoom).on("dblclick.zoom", null);

  // === Scale setup for node size and opacity ===
  const declExtent = d3.extent(data.nodes.map(d => d.decl_count || d.usage_count || 0));
  const sizeScale = d3.scaleSqrt().domain(declExtent).range([3, 14]);
  const opacityScale = d3.scaleLinear().domain(declExtent).range([0.3, 1.0]);

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
    .attr("r", d => sizeScale(d.decl_count || d.usage_count || 1))
    .attr("fill", d => colorByType(d.type))
    .attr("stroke", "#fff")
    .attr("stroke-width", 0.5)
    .attr("opacity", d => opacityScale(d.decl_count || d.usage_count || 0.5))
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended))
    .on("click", (event, d) => {
      event.stopPropagation();
      // toggle node selection
      selectedNode = selectedNode && selectedNode.id === d.id ? null : d;
      updateHighlight();
      tooltip.show(event, d);
      if (onNodeClick) onNodeClick(d);
    });

  // === Tooltip hover logic ===
  node
    .on("mouseover", (event, d) => {
      tooltip.show(event, d);
      if (!selectedNode) highlight(d);
    })
    .on("mousemove", (event) => tooltip.move(event))
    .on("mouseout", () => {
      tooltip.hide();
      if (!selectedNode) resetHighlight();
    });

  // === Background click resets selection ===
  svg.on("click", (event) => {
    if (event.target.tagName === "svg") {
      selectedNode = null;
      resetHighlight();
      tooltip.hide();
    }
  });

  // === Keyboard shortcuts ===
  window.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      selectedNode = null;
      resetHighlight();
      tooltip.hide();
    } else if (e.key === "0") {
      svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
    }
  });

  // === Highlight helpers ===
  function isConnected(a, b) {
    return data.links.some(l =>
      (l.source.id === a.id && l.target.id === b.id) ||
      (l.source.id === b.id && l.target.id === a.id)
    );
  }

  function highlight(main) {
    node
      .attr("opacity", o => (o.id === main.id || isConnected(o, main)) ? 1.0 : 0.2)
      .attr("stroke", o => (o.id === main.id ? "#fff" : null))
      .attr("stroke-width", o => (o.id === main.id ? 2 : 0.5));

    link
      .attr("stroke-opacity", l => (l.source.id === main.id || l.target.id === main.id) ? 1 : 0.05)
      .attr("stroke-width", l => (l.source.id === main.id || l.target.id === main.id) ? 2.5 : 0.8);
  }

  function resetHighlight() {
    node
      .attr("opacity", d => opacityScale(d.decl_count || d.usage_count || 0.5))
      .attr("stroke", "#fff")
      .attr("stroke-width", 0.5);
    link
      .attr("stroke-opacity", 0.4)
      .attr("stroke-width", d => (d.type === "matches" ? 1.5 : 0.8));
  }

  function updateHighlight() {
    if (selectedNode) highlight(selectedNode);
    else resetHighlight();
  }

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