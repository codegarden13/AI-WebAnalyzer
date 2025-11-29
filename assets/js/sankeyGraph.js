/**
 * sankeyGraph.js — Semi-Sankey Flow Graph with Property Clustering
 * -------------------------------------------------------------------------
 * Layout:
 *    FILES  →  SELECTORS  →  [PROP CLUSTER 1] [PROP CLUSTER 2] [PROP CLUSTER 3]
 *
 * Improvements:
 *  • Properties grouped dynamically by incoming usage count (Low/Med/High)
 *  • Cluster count fixed to 3 (customizable)
 *  • Columns adapt to number of clusters
 *  • Headers include usage ranges (e.g. “Usage 0–4”)
 *  • Smooth cubic Bézier links ("Sankey style")
 *  • Thickness reflects declaration/usage intensity
 *  • ForceGraph remains unaffected
 * -------------------------------------------------------------------------
 */

import { colorByType } from "./color.js";
import { enableZoom } from "./zoom.js";
import { setupInfoPanel } from "./infoPanel.js";
import { clusterPropertiesByUsage } from "./clusterPropertiesByUsage.js";

const infoPanel = setupInfoPanel();

export async function renderSankeyGraph(data, container) {

  // -----------------------------------------------------------
  // CLEAN PREVIOUS RENDER
  // -----------------------------------------------------------
  container.innerHTML = "";

  const width  = container.clientWidth;
  const height = container.clientHeight;

  const rowGap     = 22;
  const topOffset  = 60;
  const headerY    = 24;

  // -----------------------------------------------------------
  // SVG ROOT
  // -----------------------------------------------------------
  const svg = d3.select(container)
    .append("svg")
    .attr("width",  "100%")
    .attr("height", "100%")
    .style("background", "#111");

  const g = svg.append("g").attr("class", "sankey-root");


  // -----------------------------------------------------------
  // COPY NODES (do NOT mutate original forceGraph nodes)
  // -----------------------------------------------------------
  const nodes = data.nodes.map(n => ({ ...n }));

  const links = data.links.map(l => ({
    source: (typeof l.source === "object" ? l.source.id : l.source),
    target: (typeof l.target === "object" ? l.target.id : l.target),
    type: l.type
  }));


  // -----------------------------------------------------------
  // GROUP BY TYPE
  // -----------------------------------------------------------
  const files     = nodes.filter(n => n.type === "file");
  const selectors = nodes.filter(n => n.type === "selector");
  const rawProps  = nodes.filter(n => n.type === "property");
  const htmlNodes = nodes.filter(n => n.type === "html");


  // -----------------------------------------------------------
  // PROPERTY CLUSTERING (3 quantile groups)
  // -----------------------------------------------------------
  const propClusters = clusterPropertiesByUsage(rawProps, data.links, 3);

  /*
    propClusters = [
      { label: "Usage 0–4", items: [...] },
      { label: "Usage 5–18", items: [...] },
      { label: "Usage 19–100", items: [...] }
    ]
  */

  // total columns = files | selectors | clusters...
  const totalCols = 2 + propClusters.length;
  const colWidth  = width / totalCols;


  // -----------------------------------------------------------
  // HEADERS: Files | Selectors | Usage clusters...
  // -----------------------------------------------------------
  const headerData = [
    { text: "FILES",     x: colWidth * 0.5 },
    { text: "SELECTORS", x: colWidth * 1.5 },
    ...propClusters.map((c, i) => ({
      text: c.label,
      x: colWidth * (2 + i + 0.5)
    }))
  ];

  g.append("g")
    .attr("class", "sankey-headers")
    .selectAll("text")
    .data(headerData)
    .enter()
    .append("text")
    .text(d => d.text)
    .attr("x", d => d.x)
    .attr("y", headerY)
    .attr("fill", "#fff")
    .attr("font-size", 14)
    .attr("text-anchor", "middle")
    .attr("font-weight", 600)
    .style("letter-spacing", "0.05em");


  // -----------------------------------------------------------
  // NODE POSITIONING
  // -----------------------------------------------------------
  function positionNodes(list, colIndex) {
    const x = colIndex * colWidth + colWidth * 0.5;

    list.forEach((n, i) => {
      n.x = x;
      n.y = topOffset + i * rowGap;
      n.fx = n.x;
      n.fy = n.y;
    });
  }

  // Files (col 0)
  positionNodes(files, 0);

  // Selectors (col 1)
  positionNodes(selectors, 1);

  // Property clusters (col 2+)
  propClusters.forEach((cluster, i) => {
    positionNodes(cluster.items, 2 + i);
  });

  // HTML nodes hidden but toggleable
  htmlNodes.forEach(n => {
    n.x = n.fx = -9999;
    n.y = n.fy = -9999;
  });


  // -----------------------------------------------------------
  // LOOKUP MAP
  // -----------------------------------------------------------
  const byId = new Map(nodes.map(n => [n.id, n]));


  // -----------------------------------------------------------
  // PREPARE LINKS
  // -----------------------------------------------------------
  const preparedLinks = links
    .map(l => {
      const src = byId.get(l.source);
      const tgt = byId.get(l.target);
      if (!src || !tgt) return null;

      const weight =
        ((src.decl_count || 1) + (tgt.usage_count || 1)) * 0.20;

      return {
        source: src,
        target: tgt,
        type: l.type,
        weight: Math.max(1, Math.min(weight, 10))
      };
    })
    .filter(Boolean);


  // -----------------------------------------------------------
  // DRAW CURVED LINKS (CUBIC BÉZIER)
  // -----------------------------------------------------------
  const link = g.append("g")
    .attr("class", "sankey-links")
    .selectAll("path")
    .data(preparedLinks)
    .enter()
    .append("path")
    .attr("fill", "none")
    .attr("stroke", d => colorByType(d.type))
    .attr("stroke-width", d => d.weight)
    .attr("stroke-opacity", 0.35)
    .attr("d", d => {
      const sx = d.source.x, sy = d.source.y;
      const tx = d.target.x, ty = d.target.y;
      const mx = (sx + tx) / 2;
      return `M${sx},${sy} C${mx},${sy} ${mx},${ty} ${tx},${ty}`;
    });


  // -----------------------------------------------------------
  // DRAW NODES
  // -----------------------------------------------------------
  const node = g.append("g")
    .attr("class", "sankey-nodes")
    .selectAll("circle")
    .data(nodes)
    .enter()
    .append("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", 6)
    .attr("fill", d => colorByType(d.type))
    .attr("stroke", "#fff")
    .attr("stroke-width", 0.45)
    .style("cursor", "pointer")
    .on("mouseover", (_, d) => infoPanel.show(d))
    .on("mouseout", () => infoPanel.clear())
    .on("click", (_, d) => infoPanel.showPinned(d));


  // -----------------------------------------------------------
  // RIGHT-SIDE LABELS
  // -----------------------------------------------------------
  g.append("g")
    .attr("class", "sankey-labels")
    .selectAll("text")
    .data(nodes)
    .enter()
    .append("text")
    .attr("x", d => d.x + 10)
    .attr("y", d => d.y + 3)
    .attr("fill", "#ccc")
    .attr("font-size", 11)
    .attr("font-family", "monospace")
    .attr("text-anchor", "start")
    .text(d => {
      const t = d.label || d.id;
      return t.length > 40 ? t.slice(0, 40) + "…" : t;
    })
    .style("pointer-events", "none");


  // -----------------------------------------------------------
  // ENABLE ZOOM
  // -----------------------------------------------------------
  enableZoom(svg, g);


  // -----------------------------------------------------------
  // PUBLIC API
  // -----------------------------------------------------------
  return {
    svg,

    destroy() { svg.remove(); },

    toggleType(type, visible) {
      node
        .filter(d => d.type === type)
        .transition().duration(180)
        .style("opacity", visible ? 1 : 0);

      link
        .transition().duration(180)
        .style("opacity", l => {
          const hit = l.source.type === type || l.target.type === type;
          return hit ? (visible ? 0.35 : 0) : 0.35;
        });
    }
  };
}