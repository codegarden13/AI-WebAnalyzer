// main.js — Orchestrator
import { renderGraph } from './graph.js';
import { initLegend } from './legend.js';
import { applyFilter } from './filter.js';

document.addEventListener("DOMContentLoaded", () => {
  const graphContainer = d3.select("#graph");
  const filterInput = document.getElementById("filterInput");

  const GRAPH_FILE = "./css_graph_with_html.json";

  let allNodes = [];
  let allLinks = [];
  let svg = null;

  function loadGraph() {
    fetch(GRAPH_FILE)
      .then(r => {
        if (!r.ok) throw new Error(`Graph file not found: ${GRAPH_FILE}`);
        return r.json();
      })
      .then(data => {
        console.log(`✅ Loaded graph with ${data.nodes.length} nodes, ${data.links.length} links.`);
        const result = renderGraph(data, graphContainer);
        allNodes = result.nodes;
        allLinks = result.links;
        svg = result.svg;

        // init legend mit Callback
        initLegend(handleGroupToggle);
      })
      .catch(err => {
        console.error("🚨 Error loading graph:", err);
        document.body.innerHTML += `<div style="color:red;position:fixed;top:40%;left:40%">❌ ${err.message}</div>`;
      });
  }

  // Gruppe ein-/ausblenden
  function handleGroupToggle(group, visible) {
    console.log(`👁 Toggle group ${group}: ${visible}`);

    // Knoten filtern
    svg.selectAll("circle")
      .filter(d => d.type === group)
      .transition()
      .duration(300)
      .style("opacity", visible ? 1 : 0)
      .style("pointer-events", visible ? "all" : "none");

    // Links ausblenden, wenn eine der Enden unsichtbar ist
    svg.selectAll("line")
      .transition()
      .duration(300)
      .style("opacity", link => {
        const srcHidden = !isNodeVisible(link.source);
        const tgtHidden = !isNodeVisible(link.target);
        return (srcHidden || tgtHidden) ? 0 : 0.4;
      });
  }

  function isNodeVisible(node) {
    const el = svg.selectAll("circle").filter(d => d.id === node.id);
    return +el.style("opacity") > 0.1;
  }

  // Filterfeld
  //filterInput.addEventListener("input", e => applyFilter(e.target.value));


  filterInput.addEventListener("input", e => {
    const value = e.target.value.trim();
    applyFilter(value);     // filter graph nodes
    showMatches(value);     // filter CSS lines
  });

  // initial
  loadGraph();
});