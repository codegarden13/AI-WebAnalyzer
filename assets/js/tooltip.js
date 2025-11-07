export function setupTooltip() {
  const tooltip = d3.select("body")
    .append("div")
    .style("position", "absolute")
    .style("padding", "6px 10px")
    .style("background", "rgba(0,0,0,0.8)")
    .style("color", "white")
    .style("border-radius", "6px")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .style("opacity", 0);

  return {
    show: (event, d) => {
      tooltip.transition().duration(100).style("opacity", 1);
      tooltip.html(`<strong>${d.label}</strong><br>Type: ${d.type}`);
    },
    move: event => tooltip
      .style("left", (event.pageX + 10) + "px")
      .style("top", (event.pageY - 10) + "px"),
    hide: () => tooltip.transition().duration(100).style("opacity", 0)
  };
}