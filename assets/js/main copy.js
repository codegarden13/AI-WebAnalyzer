// main.js — unified controller with graph-type switching + transitions

import { renderForceGraph } from "./forceGraph.js";
import { renderSankeyGraph } from "./sankeyGraph.js";
import { renderColumnsView } from "./columnsView.js";

import { initLegend } from "./legend.js";
import { applyFilter } from "./filter.js";
import { updateTable } from "./table.js";

import { getGraphDescription } from "./graphDescriptions.js";

let graphData = null;
let currentRenderer = null;

/* -----------------------------------------------------------
   Helper: Remove pinned positions (fx/fy) before force layout
----------------------------------------------------------- */
function releaseFixedPositions(data) {
  data.nodes.forEach(n => {
    delete n.fx;
    delete n.fy;
  });
}

/* -----------------------------------------------------------
   Smooth fade transition between graph views
----------------------------------------------------------- */
async function smoothTransition(container, renderFn) {
  return new Promise(resolve => {
    container.style.opacity = 0;

    setTimeout(async () => {
      container.innerHTML = "";       // Clear SVG + content
      await renderFn();               // Render new graph view

      requestAnimationFrame(() => {
        container.style.opacity = 1;
        resolve();
      });
    }, 250);
  });
}

/* -----------------------------------------------------------
   MAIN
----------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", async () => {

  const graphContainer = document.getElementById("graph");
  const filterInput     = document.getElementById("filterInput");
  const graphTypeSelect = document.getElementById("graphType");
  const descBox         = document.getElementById("graphDescription");

  /* -----------------------------------------------------------
     Load combined.css for regex → results table
  ----------------------------------------------------------- */
  let cssLines = [];
  try {
    const cssText = await fetch("./combined.css").then(r => r.text());
    cssLines = cssText.split("\n");
  } catch (err) {
    console.warn("⚠ Could not load combined.css for table view");
  }

  /* -----------------------------------------------------------
     Load full graph JSON (including HTML nodes)
  ----------------------------------------------------------- */
  graphData = await fetch("./css_graph_with_html.json").then(r => r.json());
  console.log("Graph loaded:", graphData);

  /* -----------------------------------------------------------
     Initial view: FORCE GRAPH
  ----------------------------------------------------------- */
  updateGraphDescription("force");
  await renderView("force");

  /* -----------------------------------------------------------
     Legend toggle
  ----------------------------------------------------------- */
  initLegend((type, visible) => {
    if (currentRenderer?.toggleType) {
      currentRenderer.toggleType(type, visible);
    }
  });

  /* -----------------------------------------------------------
     Regex filter → graph + table
  ----------------------------------------------------------- */
  filterInput.addEventListener("input", e => {
    const regex = e.target.value.trim();
    applyFilter(regex);
    updateTable(regex, cssLines);
  });

  /* -----------------------------------------------------------
     Switch graph types from dropdown
  ----------------------------------------------------------- */
  graphTypeSelect.addEventListener("change", async e => {
    const mode = e.target.value;
    updateGraphDescription(mode);
    await renderView(mode);
  });

  /* -----------------------------------------------------------
     Update description box based on graph type
  ----------------------------------------------------------- */
  function updateGraphDescription(type) {
    descBox.innerHTML = getGraphDescription(type);
  }

  /* -----------------------------------------------------------
     Render view hub (force, sankey, columns)
  ----------------------------------------------------------- */
  async function renderView(mode) {
    const container = graphContainer;

    await smoothTransition(container, async () => {

      // IMPORTANT: allow force graph to animate again
      if (mode === "force") {
        releaseFixedPositions(graphData);
      }

      if (mode === "force") {
        currentRenderer = await renderForceGraph(graphData, container);
      }
      else if (mode === "sankey") {
        currentRenderer = await renderSankeyGraph(graphData, container);
      }
      else if (mode === "columns") {
        currentRenderer = await renderColumnsView(graphData, container);
      }
    });
  }

});