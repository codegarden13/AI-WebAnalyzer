// clusterSelectors.js
// ------------------------------------------------------------
// Provides two clustering modes for selectors:
//  1) Cluster by file origin ("file")
//  2) Cluster by semantic meaning ("semantic")
// Also includes automatic multi-column splitting.
// ------------------------------------------------------------

/**
 * Cluster entry point.
 */
export function clusterSelectors(selectors, mode = "file", maxPerColumn = 55) {
  let groups = [];

  if (mode === "file") {
    groups = clusterByFile(selectors);
  } else if (mode === "semantic") {
    groups = clusterBySemantic(selectors);
  } else {
    console.warn("Unknown cluster mode:", mode);
    groups = clusterByFile(selectors);
  }

  // Split large groups into subcolumns
  return splitLargeGroups(groups, maxPerColumn);
}

// ------------------------------------------------------------
// 1) CLUSTER BY FILE ORIGIN
// ------------------------------------------------------------
export function clusterByFile(selectors) {
  const buckets = {};

  selectors.forEach(sel => {
    const file = sel.file || "unknown";
    if (!buckets[file]) buckets[file] = [];
    buckets[file].push(sel);
  });

  // Convert to array with group labels
  return Object.entries(buckets).map(([file, items]) => ({
    label: file,
    items: items.sort((a, b) => a.label.localeCompare(b.label))
  }));
}

// ------------------------------------------------------------
// 2) CLUSTER BY SEMANTIC MEANING
// ------------------------------------------------------------
export function clusterBySemantic(selectors) {

  const groups = {
    COMPONENTS: [],
    LAYOUT: [],
    UTILITIES: [],
    TYPOGRAPHY: [],
    STATE: [],
    RESET: [],
    MISC: []
  };

  selectors.forEach(sel => {
    const s = sel.label;

    // Components
    if (/btn|button|card|modal|hero|nav|menu|dropdown|footer|header/i.test(s)) {
      groups.COMPONENTS.push(sel);
    }
    // Layout / structure
    else if (/grid|row|col|container|wrapper|section|flex|layout/i.test(s)) {
      groups.LAYOUT.push(sel);
    }
    // Utility classes
    else if (/^u-|^util-|--|margin|pad|mt-|pt-|ml-|pl-|text-|bg-|color-/i.test(s)) {
      groups.UTILITIES.push(sel);
    }
    // Typography
    else if (/^h[1-6]$|title|subtitle|text-|font-|bold|italic/i.test(s)) {
      groups.TYPOGRAPHY.push(sel);
    }
    // State selectors
    else if (/:hover|:active|:checked|\.is-|\.has-|\.open|\.active/i.test(s)) {
      groups.STATE.push(sel);
    }
    // Reset / normalizer rules
    else if (/^\*|html|body|normalize|reset/i.test(s)) {
      groups.RESET.push(sel);
    }
    // Anything else
    else {
      groups.MISC.push(sel);
    }
  });

  // Convert non-empty groups
  return Object.entries(groups)
    .filter(([_, items]) => items.length > 0)
    .map(([label, items]) => ({
      label,
      items: items.sort((a, b) => a.label.localeCompare(b.label))
    }));
}

// ------------------------------------------------------------
// 3) SPLIT LARGE GROUPS INTO MULTIPLE SUBCOLUMNS
// ------------------------------------------------------------
export function splitLargeGroups(groups, maxPerColumn = 55) {
  const result = [];

  groups.forEach(group => {
    if (group.items.length <= maxPerColumn) {
      result.push(group);
      return;
    }

    // Need to split into subcolumns
    let index = 0;
    const chunks = Math.ceil(group.items.length / maxPerColumn);

    for (let c = 0; c < chunks; c++) {
      const chunkItems = group.items.slice(c * maxPerColumn, (c + 1) * maxPerColumn);

      result.push({
        label: `${group.label} (${c + 1})`,
        items: chunkItems
      });

      index++;
    }
  });

  return result;
}