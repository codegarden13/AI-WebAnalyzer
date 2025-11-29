export function setupInfoPanel() {
  const panel = document.getElementById("infoPanel");
  const content = document.getElementById("infoContent");

  return {
    show(d) {
      content.innerHTML = `
        <strong>Label:</strong> ${d.label}<br>
        <strong>Type:</strong> ${d.type}<br>
        ${d.file ? `<strong>File:</strong> ${d.file}<br>` : ""}
        ${d.selector ? `<strong>Selector:</strong> ${d.selector}<br>` : ""}
        ${d.decl_count ? `<strong>Declarations:</strong> ${d.decl_count}<br>` : ""}
        ${d.usage_count ? `<strong>Usage count:</strong> ${d.usage_count}<br>` : ""}
        ${d.specificity ? `<strong>Specificity:</strong> ${d.specificity}<br>` : ""}
        ${d.complexity ? `<strong>Complexity:</strong> ${d.complexity}<br>` : ""}
      `;
    },

    clear() {
      content.innerHTML = "Click a node to inspect it.";
    }
  };
}