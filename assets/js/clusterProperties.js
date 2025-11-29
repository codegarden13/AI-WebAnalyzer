// clusterProperties.js — semantic clustering of CSS properties
// -------------------------------------------------------------

export function clusterProperties(properties) {
  
  const groups = {
    Colors: [
      "color", "background", "background-color", "border-color",
      "box-shadow", "text-shadow", "fill", "stroke", "opacity"
    ],

    Layout: [
      "display", "position", "top", "right", "bottom", "left",
      "z-index", "float", "clear"
    ],

    Spacing: [
      "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
      "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
      "gap", "row-gap", "column-gap"
    ],

    Sizing: [
      "width", "height", "min-width", "max-width",
      "min-height", "max-height", "aspect-ratio"
    ],

    Typography: [
      "font-size", "font-family", "font-weight", "line-height",
      "letter-spacing", "text-transform", "text-align", "white-space",
      "word-break", "font-style", "text-decoration"
    ],

    Flexbox: [
      "flex", "flex-basis", "flex-grow", "flex-shrink",
      "justify-content", "align-items", "align-content",
      "flex-direction", "flex-wrap", "order"
    ],

    Grid: [
      "grid", "grid-template-columns", "grid-template-rows",
      "grid-area", "grid-gap", "grid-column", "grid-row"
    ],

    Animation: [
      "transition", "transition-duration", "transition-property",
      "animation", "animation-name", "animation-duration",
      "animation-timing-function", "transform"
    ],

    Misc: [] // Will fill dynamically
  };

  // Prepare output structure
  const result = Object.keys(groups).map(name => ({
    label: name,
    items: []
  }));

  // Normalize indexes
  const groupIndex = Object.fromEntries(
    Object.keys(groups).map((name, i) => [name, i])
  );

  // Assign properties to groups
  properties.forEach(prop => {
    const name = prop.label.toLowerCase();

    // Find matching group
    let assigned = false;
    for (const groupName in groups) {
      if (groups[groupName].some(g => name.startsWith(g))) {
        const idx = groupIndex[groupName];
        result[idx].items.push(prop);
        assigned = true;
        break;
      }
    }

    // Unmatched → Misc
    if (!assigned) {
      const idx = groupIndex["Misc"];
      result[idx].items.push(prop);
    }
  });

  // Remove empty groups
  return result.filter(g => g.items.length > 0);
}