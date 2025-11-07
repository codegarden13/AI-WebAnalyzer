export function enableZoom(svg, g) {
  const zoom = d3.zoom()
    .scaleExtent([0.25, 4])
    .on("zoom", e => g.attr("transform", e.transform));

  svg.call(zoom).on("dblclick.zoom", null);

  // Reset zoom with "0"
  window.addEventListener("keydown", e => {
    if (e.key === "0") svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
  });
}