// main.js — unified controller with graph-type + cluster switching

import { renderForceGraph } from "./forceGraph.js";
import { renderSankeyGraph } from "./sankeyGraph.js";
import { renderColumnsView } from "./columnsView.js";

import { initLegend } from "./legend.js";
import { applyFilter } from "./filter.js";
import { updateTable } from "./table.js";
import { getGraphDescription } from "./graphDescriptions.js";

let graphData = null;
let currentRenderer = null;
let currentGraphType = "force";
let currentClusterMode = "file";   // NEW

// Smooth fade transition
async function smoothTransition(container, renderFn) {
  return new Promise(resolve => {
    container.style.opacity = 0;

    setTimeout(async () => {
      container.innerHTML = "";
      await renderFn();
      requestAnimationFrame(() => {
        container.style.opacity = 1;
        resolve();
      });
    }, 200);
  });
}

document.addEventListener("DOMContentLoaded", async () => {

  const graphContainer = document.getElementById("graph");
  const filterInput     = document.getElementById("filterInput");
  const graphTypeSelect = document.getElementById("graphType");
  const clusterSelect   = document.getElementById("clusterMode");
  const descBox         = document.getElementById("graphDescription");

  // Load CSS lines for regex table
  let cssLines = [];
  try {
    const cssText = await fetch("./combined.css").then(r => r.text());
    cssLines = cssText.split("\n");
  } catch (e) {
    console.warn("⚠ Could not load combined.css for table view");
  }

  // Load graph JSON
  graphData = await fetch("./css_graph_with_html.json").then(r => r.json());

  // Render initial view
  updateGraphDescription("force");
  await renderView("force", currentClusterMode);

  // Legend toggle
  initLegend((type, visible) => {
    currentRenderer?.toggleType?.(type, visible);
  });

  // Regex filtering
  filterInput.addEventListener("input", e => {
    const regex = e.target.value.trim();
    applyFilter(regex);
    updateTable(regex, cssLines);
  });

  // --- Graph type switching ---
  graphTypeSelect.addEventListener("change", async e => {
    currentGraphType = e.target.value;
    updateGraphDescription(currentGraphType);
    await renderView(currentGraphType, currentClusterMode);
  });

  // --- Cluster mode switching ---
  clusterSelect.addEventListener("change", async e => {
    currentClusterMode = e.target.value;

    // Only re-render if graph supports clustering
    if (currentGraphType === "columns" || currentGraphType === "sankey") {
      await renderView(currentGraphType, currentClusterMode);
    }
  });

  // Helper to render correct graph
  async function renderView(graphType, clusterMode) {

    await smoothTransition(graphContainer, async () => {

      if (graphType === "force") {
        currentRenderer = await renderForceGraph(graphData, graphContainer);
        return;
      }

      if (graphType === "columns") {
        currentRenderer = await renderColumnsView(graphData, graphContainer, clusterMode);
        return;
      }

      if (graphType === "sankey") {
        currentRenderer = await renderSankeyGraph(graphData, graphContainer, clusterMode);
        return;
      }
    });
  }

  function updateGraphDescription(type) {
    descBox.innerHTML = getGraphDescription(type);
  }
});