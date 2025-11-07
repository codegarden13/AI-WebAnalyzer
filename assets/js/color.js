export function colorByType(type) {
  switch (type) {
    case "file": return "#ff9800";
    case "selector": return "#03a9f4";
    case "property": return "#4caf50";
    case "html": return "#e91e63";
    case "matches": return "#e91e63";
    case "defines": return "#ff9800";
    case "uses": return "#4caf50";
    default: return "#999";
  }
}