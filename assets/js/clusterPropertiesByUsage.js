// clusterPropertiesByUsage.js
// -----------------------------------------------------------------------------
// Groups property nodes into N buckets based on how often they are used.
// Each bucket gets:
//   { label: "Usage min–max", items: [propertyNodes...] }
// -----------------------------------------------------------------------------


/**
 * Cluster properties into usage buckets.
 *
 * @param {Array} properties  Array of nodes with type === "property"
 * @param {Array} links       Full graph links (we'll count uses → properties)
 * @param {number} bucketCount  Desired number of buckets (default 3)
 * @returns {Array<{label: string, items: Array}>}
 */
export function clusterPropertiesByUsage(properties, links, bucketCount = 3) {
  if (!properties || properties.length === 0) {
    return [];
  }

  // 1) Count how often each property is used (incoming "uses" links)
  const usageMap = new Map();

  links.forEach(l => {
    const type = l.type || l.linkType || l.kind;
    if (type !== "uses") return;

    const targetId = typeof l.target === "object" ? l.target.id : l.target;
    if (!targetId || !targetId.startsWith("prop::")) return;

    const prev = usageMap.get(targetId) || 0;
    usageMap.set(targetId, prev + 1);
  });

  // 2) Attach usage to nodes (fallback 0)
  const enriched = properties.map(p => {
    const usage = usageMap.get(p.id) || p.usage_count || 0;
    return { ...p, _usageScore: usage };
  });

  // 3) Sort by usage (highest first works nicely for bucketing)
  enriched.sort((a, b) => b._usageScore - a._usageScore);

  // If fewer properties than buckets → reduce bucketCount
  const effectiveBuckets = Math.min(bucketCount, Math.max(1, enriched.length));
  if (effectiveBuckets === 1) {
    const minU = enriched[enriched.length - 1]._usageScore;
    const maxU = enriched[0]._usageScore;
    return [{
      label: `Usage ${minU}–${maxU}`,
      items: enriched
    }];
  }

  // 4) Slice into roughly equal buckets
  const bucketSize = Math.ceil(enriched.length / effectiveBuckets);
  const clusters = [];

  for (let i = 0; i < effectiveBuckets; i++) {
    const start = i * bucketSize;
    const end   = Math.min(start + bucketSize, enriched.length);
    if (start >= enriched.length) break;

    const slice = enriched.slice(start, end);
    if (slice.length === 0) continue;

    const usageValues = slice.map(p => p._usageScore);
    const minU = Math.min(...usageValues);
    const maxU = Math.max(...usageValues);

    clusters.push({
      label: `Usage ${minU}–${maxU}`,
      items: slice
    });
  }

  // Debug in console so you can see the split
  console.log("🔎 Property clusters:", clusters.map(c => ({
    label: c.label,
    count: c.items.length
  })));

  return clusters;
}