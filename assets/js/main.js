// main.js — Orchestrator
import { renderGraph } from './graph.js';
import { initLegend } from './legend.js';
import { applyFilter } from './filter.js';
import { updateTable } from './table.js';   // ← MUSS ganz oben stehen!

let combinedCssLines = [];
let currentGraph = null;

document.addEventListener("DOMContentLoaded", async () => {
  const graphContainer = d3.select("#graph");
  const filterInput = document.getElementById("filterInput");

  // ---------------------------------------------------------
  // 1) combined.css laden (für Tabellensuche)
  // ---------------------------------------------------------
  try {
    const cssText = await fetch("./combined.css").then(r => r.text());
    combinedCssLines = cssText.split("\n");
    console.log("📄 Loaded combined.css with", combinedCssLines.length, "lines.");
  } catch (err) {
    console.error("❌ Could not load combined.css:", err);
  }

  // ---------------------------------------------------------
  // 2) Graph JSON laden
  // ---------------------------------------------------------
  const GRAPH_FILE = "./css_graph_with_html.json";

  try {
    const data = await fetch(GRAPH_FILE).then(r => {
      if (!r.ok) throw new Error("Graph file not found");
      return r.json();
    });
    console.log(`✅ Loaded graph with ${data.nodes.length} nodes, ${data.links.length} links.`);
    currentGraph = data;

    // Graph rendern
    renderGraph(data, graphContainer);

    // Legende initialisieren
    initLegend(handleGroupToggle);

  } catch (err) {
    console.error("🚨 Error loading graph:", err);
    document.body.innerHTML += `<div style="color:red;position:fixed;top:40%;left:40%">❌ ${err.message}</div>`;
  }

  // ---------------------------------------------------------
  // 3) Filter verbinden (Graph + Tabelle)
  // ---------------------------------------------------------
  filterInput.addEventListener("input", e => {
    const pattern = e.target.value;

    // Filter Graph Nodes
    applyFilter(pattern);

    // Filter CSS Table
    updateTable(pattern, combinedCssLines);
  });
});


// -------------------------------------------------------------
// Gruppe per Checkbox ein-/ausblenden
// -------------------------------------------------------------
function handleGroupToggle(group, visible) {
  console.log(`👁 Toggle group ${group}: ${visible}`);

  const svg = d3.select("svg");

  // Knoten filtern
  svg.selectAll("circle")
    .filter(d => d.type === group)
    .transition()
    .duration(300)
    .style("opacity", visible ? 1 : 0)
    .style("pointer-events", visible ? "all" : "none");

  // Links filtern
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
  const el = d3.selectAll("circle").filter(d => d.id === node.id);
  return +el.style("opacity") > 0.1;
}