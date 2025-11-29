// columnsView.js — Clustered multi-column visualization (selectors + properties)
// ------------------------------------------------------------------------------
// Features:
// • Files → Selector Clusters → Property Clusters
// • clusterMode: "file" | "semantic"
// • Semantic property clusters (Colors, Layout, Typography …)
// • Multi-column layout based on number of clusters
// • InfoPanel support
// • Shared zoom
// ------------------------------------------------------------------------------

import { colorByType } from "./color.js";
import { enableZoom } from "./zoom.js";
import { setupInfoPanel } from "./infoPanel.js";
import { clusterSelectors } from "./clusterSelectors.js";
import { clusterProperties } from "./clusterProperties.js";

const infoPanel = setupInfoPanel();

export function renderColumnsView(data, container, clusterMode = "file") {

  container.innerHTML = "";

  const width  = container.clientWidth;
  const height = container.clientHeight;

  const rowHeight  = 22;
  const topOffset  = 60;

  // ---------------------------------------------------------
  // SVG root
  // ---------------------------------------------------------
  const svg = d3.select(container)
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .style("background", "#111");

  const g = svg.append("g").attr("class", "columns-root");

  // ---------------------------------------------------------
  // 1) Separate node types
  // ---------------------------------------------------------
  const files     = data.nodes.filter(n => n.type === "file");
  const selectors = data.nodes.filter(n => n.type === "selector");
  const props     = data.nodes.filter(n => n.type === "property");
  const htmlNodes = data.nodes.filter(n => n.type === "html"); // hidden

  // ---------------------------------------------------------
  // 2) Cluster selectors
  // ---------------------------------------------------------
  const selectorClusters = clusterSelectors(selectors, clusterMode);

  // ---------------------------------------------------------
  // 3) Cluster properties (new!)
  // ---------------------------------------------------------
  const propertyClusters = clusterProperties(props);

  const selectorCols = selectorClusters.length;
  const propertyCols = propertyClusters.length;

  // Final column count:
  // FILES | selector clusters... | property clusters...
  const totalCols = 1 + selectorCols + propertyCols;
  const colWidth  = width / totalCols;

  // ---------------------------------------------------------
  // 4) Node positioning helper
  // ---------------------------------------------------------
  function position(nodes, colIndex) {
    const x = colIndex * colWidth + colWidth * 0.5;

    nodes.forEach((n, i) => {
      n.fx = x;
      n.fy = topOffset + i * rowHeight;
    });
  }

  // Position file nodes
  position(files, 0);

  // Position selectors by cluster
  selectorClusters.forEach((cl, idx) => {
    position(cl.items, 1 + idx);
  });

  // Position property clusters
  propertyClusters.forEach((cl, idx) => {
    position(cl.items, 1 + selectorCols + idx);
  });

  // Hide HTML nodes
  htmlNodes.forEach(n => { n.fx = -9999; n.fy = -9999; });

  // ---------------------------------------------------------
  // 5) Column headers
  // ---------------------------------------------------------
  const headerData = [
    { text: "Files", x: colWidth * 0.5 },

    ...selectorClusters.map((cl, i) => ({
      text: cl.label,
      x: colWidth * (1 + i + 0.5)
    })),

    ...propertyClusters.map((cl, i) => ({
      text: cl.label,
      x: colWidth * (1 + selectorCols + i + 0.5)
    }))
  ];

  g.append("g")
    .attr("class", "column-headers")
    .selectAll("text")
    .data(headerData)
    .enter()
    .append("text")
    .attr("x", d => d.x)
    .attr("y", 26)
    .attr("text-anchor", "middle")
    .attr("fill", "#fff")
    .attr("font-weight", "600")
    .attr("font-size", 14)
    .text(d => d.text);

  // ---------------------------------------------------------
  // 6) Link mapping
  // ---------------------------------------------------------
  const nodeById = new Map(data.nodes.map(n => [n.id, n]));

  const preparedLinks = data.links.map(l => {
    const srcId = typeof l.source === "object" ? l.source.id : l.source;
    const tgtId = typeof l.target === "object" ? l.target.id : l.target;

    const s = nodeById.get(srcId);
    const t = nodeById.get(tgtId);

    if (!s || !t) return null;
    if (s.fx == null || t.fx == null) return null;

    return {
      source: s,
      target: t,
      type: l.type
    };
  }).filter(Boolean);

  // ---------------------------------------------------------
  // 7) Draw links
  // ---------------------------------------------------------
  const link = g.append("g")
    .attr("class", "columns-links")
    .selectAll("line")
    .data(preparedLinks)
    .enter()
    .append("line")
    .attr("x1", d => d.source.fx)
    .attr("y1", d => d.source.fy)
    .attr("x2", d => d.target.fx)
    .attr("y2", d => d.target.fy)
    .attr("stroke", d => colorByType(d.type))
    .attr("stroke-opacity", 0.22)
    .attr("stroke-width", 1);

  // ---------------------------------------------------------
  // 8) Draw nodes
  // ---------------------------------------------------------
  const node = g.append("g")
    .attr("class", "columns-nodes")
    .selectAll("circle")
    .data(data.nodes)
    .enter()
    .append("circle")
    .attr("cx", d => d.fx)
    .attr("cy", d => d.fy)
    .attr("r", 6)
    .attr("fill", d => colorByType(d.type))
    .attr("stroke", "#fff")
    .attr("stroke-width", 0.5)
    .style("cursor", "pointer")
    .on("mouseover", (_, d) => infoPanel.show(d))
    .on("mouseout", () => infoPanel.clear())
    .on("click", (_, d) => infoPanel.showPinned(d));

  // ---------------------------------------------------------
  // 9) Right-side labels
  // ---------------------------------------------------------
  const label = g.append("g")
    .attr("class", "columns-labels")
    .selectAll("text")
    .data(data.nodes)
    .enter()
    .append("text")
    .attr("x", d => d.fx + 12)
    .attr("y", d => d.fy + 4)
    .attr("fill", "#ccc")
    .attr("font-size", 11)
    .attr("font-family", "system-ui, monospace")
    .text(d => truncate(d.label ?? d.id))
    .style("cursor", "pointer")
    .on("mouseover", (_, d) => infoPanel.show(d))
    .on("mouseout", () => infoPanel.clear())
    .on("click", (_, d) => infoPanel.showPinned(d));

  label.append("title").text(d => d.label ?? d.id);

  function truncate(s) {
    return s.length > 38 ? s.slice(0, 38) + "…" : s;
  }

  // ---------------------------------------------------------
  // 10) Zoom
  // ---------------------------------------------------------
  enableZoom(svg, g);

  // ---------------------------------------------------------
  // 11) Public API for main.js
  // ---------------------------------------------------------
  return {
    svg,

    destroy() { svg.remove(); },

    toggleType(type, visible) {
      const alpha = visible ? 1 : 0;

      node
        .filter(d => d.type === type)
        .transition()
        .duration(180)
        .style("opacity", alpha);

      label
        .filter(d => d.type === type)
        .transition()
        .duration(180)
        .style("opacity", alpha);

      link
        .transition()
        .duration(180)
        .style("opacity", l => {
          const hit = l.source.type === type || l.target.type === type;
          return hit ? (visible ? 0.22 : 0) : 0.22;
        });
    }
  };
}