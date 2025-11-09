// tooltip.js — Kontext-Inspector für CSS- und HTML-Nodes
export function setupTooltip() {
  const tooltip = d3.select("body")
    .append("div")
    .attr("id", "graph-tooltip")
    .style("position", "absolute")
    .style("max-width", "320px")
    .style("padding", "8px 12px")
    .style("background", "rgba(0,0,0,0.85)")
    .style("color", "#fff")
    .style("border-radius", "8px")
    .style("font-size", "12px")
    .style("line-height", "1.4")
    .style("pointer-events", "none")
    .style("box-shadow", "0 2px 8px rgba(0,0,0,0.4)")
    .style("opacity", 0)
    .style("z-index", 50);

  return {
    show: (event, d) => {
      tooltip.transition().duration(120).style("opacity", 1);

      // 🔍 Node-spezifische Informationen
      const isUnused = d.unused === true;
      const declCount = d.decl_count ?? d.usage_count ?? 0;
      const specificity = d.specificity ?? 0;
      const complexity = d.complexity ?? 0;

      // 🗂️ Quelle (Dateiname aus "file::..." ableiten, falls vorhanden)
      const fileName = d.file || extractFileName(d.id) || "Unbekannt";

      // 💬 Optionaler CSS-Text
      let cssSnippet = "";
      if (d.css_text) {
        const snippet = d.css_text.trim().slice(0, 200).replace(/\n+/g, " ");
        cssSnippet = `<pre style="margin-top:6px;padding:6px;background:rgba(255,255,255,0.08);border-radius:4px;color:#ccc;font-family:monospace;white-space:pre-wrap;">${escapeHTML(snippet)}${d.css_text.length > 200 ? " …" : ""}</pre>`;
      }

      tooltip.html(`
        <div style="margin-bottom:4px;">
          <strong style="font-size:13px;color:${isUnused ? '#888' : '#fff'}">
            ${escapeHTML(d.label)}
          </strong>
          ${isUnused ? '<span style="color:#ff6666;font-weight:bold;"> ❌ ungenutzt</span>' : ''}
        </div>

        <div style="opacity:0.85;">
          <div><b>Typ:</b> ${d.type}</div>
          <div><b>CSS-Datei:</b> ${escapeHTML(fileName)}</div>
          ${declCount ? `<div><b>Deklarationen:</b> ${declCount}</div>` : ""}
          ${specificity ? `<div><b>Spezifität:</b> ${specificity}</div>` : ""}
          ${complexity ? `<div><b>Komplexität:</b> ${complexity}</div>` : ""}
        </div>
        ${cssSnippet}
      `);
    },

    move: event => tooltip
      .style("left", (event.pageX + 12) + "px")
      .style("top", (event.pageY - 10) + "px"),

    hide: () => tooltip.transition().duration(150).style("opacity", 0)
  };
}

/* ───────────── Hilfsfunktionen ───────────── */

function escapeHTML(str) {
  return str?.replace(/[&<>"']/g, m => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]
  )) || "";
}

function extractFileName(id) {
  if (!id) return null;
  const m = id.match(/file::([^/]+\.css)/);
  return m ? m[1] : null;
}