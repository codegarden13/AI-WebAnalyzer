// legend.js — dynamic vertical legend with grouped checkboxes and unused selector support
import { colorByType } from './color.js';

export function initLegend(onToggleGroup) {
  const legendContainer = d3.select("#legend");
  legendContainer.html(""); // Clear previous content

  // === Legend groups ===
  const legendGroups = [
    {
      title: "🔹 Knotenarten",
      items: [
        { type: "file", label: "CSS-Dateien" },
        { type: "selector", label: "Selektoren (aktiv)" },
        { type: "unused", label: "❌ Unbenutzte Selektoren" },
        { type: "property", label: "Eigenschaften" },
        { type: "html", label: "HTML-Elemente" },
      ]
    },
    {
      title: "🔸 Beziehungen",
      items: [
        { type: "uses", label: "verwendet (Selector → Property)" },
        { type: "matches", label: "verknüpft (HTML ↔ CSS)" },
      ]
    }
  ];

  // === Styling for layout ===
  legendContainer
    .style("display", "flex")
    .style("flex-direction", "column")
    .style("gap", "10px")
    .style("font-size", "13px");

  // === Render groups ===
  legendGroups.forEach(group => {
    const groupDiv = legendContainer
      .append("div")
      .attr("class", "legend-group")
      .style("display", "flex")
      .style("flex-direction", "column")
      .style("gap", "4px");

    // Title
    groupDiv
      .append("div")
      .style("font-weight", "600")
      .style("margin-bottom", "2px")
      .text(group.title);

    // Items
    group.items.forEach(item => {
      const color = item.type === "unused" ? "#777" : colorByType(item.type);

      const row = groupDiv
        .append("label")
        .attr("class", "legend-item")
        .style("display", "flex")
        .style("align-items", "center")
        .style("gap", "6px")
        .style("cursor", "pointer")
        .html(`
          <input type="checkbox" data-type="${item.type}" checked>
          <i style="background:${color};width:10px;height:10px;border-radius:2px;"></i>
          <span>${item.label}</span>
        `);

      row.select("input").on("change", (event) => {
        const checked = event.target.checked;
        onToggleGroup(item.type, checked);
      });
    });

    // Add separator line between groups
    if (group.title.includes("Beziehungen")) {
      groupDiv
        .style("border-top", "1px solid rgba(255,255,255,0.2)")
        .style("padding-top", "6px");
    }
  });
}