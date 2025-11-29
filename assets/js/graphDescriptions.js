// graphDescriptions.js — dynamic usage guide per graph type

export function getGraphDescription(type) {
  switch (type) {

    case "force":
      return `
        <strong>Force Graph</strong><br>
        A physics-based layout showing the full CSS architecture:<br>
        • <strong>Files</strong> → contain selectors<br>
        • <strong>Selectors</strong> → contain properties<br>
        • <strong>HTML nodes</strong> → show selector matches (if enabled)<br><br>
        <em>Interactions:</em><br>
        – Drag to pan • Scroll to zoom • Hover for quick info • Click to inspect<br>
      `;

    case "columns":
      return `
        <strong>Columns View</strong><br>
        A structured overview where nodes are sorted by type:<br>
        • Left: <strong>CSS Files</strong><br>
        • Middle: <strong>Selectors</strong><br>
        • Right: <strong>Properties</strong><br><br>
        This layout helps identify which file owns which selectors and which
        selectors use which properties.<br><br>
        Hover or click nodes to view full details.
      `;

    case "sankey":
      return `
        <strong>Sankey Flow</strong><br>
        A flow-based representation showing how CSS cascades:<br>
        • <strong>Files → Selectors → Properties</strong> as weighted flows<br>
        • Link width reflects relationship density<br><br>
        Ideal for analyzing which files dominate the system and
        how properties propagate through selectors.<br><br>
        Hover and click nodes for details.
      `;

    default:
      return "Graph description not available.";
  }
}