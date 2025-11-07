export function applyFilter(pattern) {
  const svg = d3.select("svg");
  const node = svg.selectAll("circle");
  const link = svg.selectAll("line");

  if (!pattern.trim()) {
    node.attr("opacity", 0.9);
    link.attr("stroke-opacity", 0.5);
    return;
  }

  let regex;
  try { regex = new RegExp(pattern, "i"); }
  catch { return; }

  node.attr("opacity", d => regex.test(d.label) ? 1 : 0.1);
  link.attr("stroke-opacity", d => regex.test(d.source.label) || regex.test(d.target.label) ? 0.9 : 0.05);
}