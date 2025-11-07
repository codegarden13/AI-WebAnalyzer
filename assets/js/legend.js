// legend.js — dynamic legend with checkboxes per type
import { colorByType } from './color.js';

export function initLegend(onToggleGroup) {
  const legendContainer = d3.select("#legend");
  legendContainer.html(""); // clear any previous legend

  const groups = [
    { type: "file", label: "CSS Files" },
    { type: "selector", label: "Selectors" },
    { type: "property", label: "Properties" },
    { type: "html", label: "HTML Elements" },
  ];

  groups.forEach(g => {
    const item = legendContainer
      .append("label")
      .attr("class", "legend-item")
      .style("display", "flex")
      .style("align-items", "center")
      .style("gap", "4px")
      .style("cursor", "pointer")
      .html(`
        <input type="checkbox" data-type="${g.type}" checked>
        <i style="background:${colorByType(g.type)};width:10px;height:10px;border-radius:2px;"></i>
        <span>${g.label}</span>
      `);

    item.select("input").on("change", (event) => {
      const checked = event.target.checked;
      onToggleGroup(g.type, checked);
    });
  });
}