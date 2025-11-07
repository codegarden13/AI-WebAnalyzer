"""
graph_builder.py
──────────────────────────────────────────────
Builds an enriched graph representation of CSS:
- file → selector → property relationships
- declaration / usage metrics
- basic complexity and specificity analysis
- ready for D3 visualization and audits
"""

import datetime
import re
from typing import Dict, Any, List


def build_css_graph(
    css_files: Dict[str, str],
    cssutils_rules: List[Dict[str, Any]],
    tinycss_rules: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a graph of CSS relationships (files → selectors → properties),
    enriched with declaration/usage metrics and selector complexity.
    """
    nodes, links = [], []
    selector_set, prop_set = set(), set()

    # ───────────────────────────────
    # 1️⃣ File nodes
    # ───────────────────────────────
    for f in css_files.keys():
        nodes.append({
            "id": f"file::{f}",
            "type": "file",
            "label": f,
            "group": 1
        })

    # ───────────────────────────────
    # 2️⃣ Selector & property nodes
    # ───────────────────────────────
    for rule in cssutils_rules:
        if rule["type"] != "style":
            continue
        sel = rule["selector"]
        if not sel:
            continue

        # add selector node once
        if sel not in selector_set:
            selector_set.add(sel)
            nodes.append({
                "id": f"sel::{sel}",
                "type": "selector",
                "label": sel,
                "group": 2,
                "specificity": _estimate_specificity(sel),
                "complexity": _estimate_complexity(sel),
            })

        # add property nodes + uses links
        for d in rule["declarations"]:
            prop = d["property"]
            if not prop:
                continue
            if prop not in prop_set:
                prop_set.add(prop)
                nodes.append({
                    "id": f"prop::{prop}",
                    "type": "property",
                    "label": prop,
                    "group": 3,
                })
            links.append({
                "source": f"sel::{sel}",
                "target": f"prop::{prop}",
                "type": "uses",
            })

    # ───────────────────────────────
    # 3️⃣ File → selector links
    # ───────────────────────────────
    for f, text in css_files.items():
        for s in selector_set:
            # heuristic: selector string appears in text
            if s in text:
                links.append({
                    "source": f"file::{f}",
                    "target": f"sel::{s}",
                    "type": "defines"
                })

    # ───────────────────────────────
    # 4️⃣ Compute per-node metrics
    # ───────────────────────────────
    for node in nodes:
        if node["type"] == "selector":
            decl_count = sum(1 for l in links if l["source"] == node["id"] and l["type"] == "uses")
            node["decl_count"] = decl_count
            node["score"] = node["complexity"] + node["specificity"] + decl_count
        elif node["type"] == "property":
            usage_count = sum(1 for l in links if l["target"] == node["id"] and l["type"] == "uses")
            node["usage_count"] = usage_count

    # ───────────────────────────────
    # 5️⃣ Build summary meta data
    # ───────────────────────────────
    return {
        "meta": {
            "generated": datetime.datetime.utcnow().isoformat() + "Z",
            "files": len(css_files),
            "selectors": len(selector_set),
            "properties": len(prop_set),
            "total_links": len(links),
            "avg_complexity": round(sum(n.get("complexity", 0) for n in nodes if n["type"] == "selector") / (len(selector_set) or 1), 2),
            "avg_specificity": round(sum(n.get("specificity", 0) for n in nodes if n["type"] == "selector") / (len(selector_set) or 1), 2),
        },
        "nodes": nodes,
        "links": links,
    }


# ───────────────────────────────
# Helper metrics
# ───────────────────────────────

def _estimate_specificity(selector: str) -> int:
    """Rough specificity score based on CSS selector tokens."""
    id_count = selector.count("#")
    class_count = selector.count(".")
    attr_count = selector.count("[")
    pseudo_class_count = selector.count(":") - selector.count("::")
    return id_count * 100 + (class_count + attr_count + pseudo_class_count) * 10


def _estimate_complexity(selector: str) -> int:
    """Estimate complexity based on combinators and nesting depth."""
    return len(re.findall(r"[ >+~]", selector)) + selector.count(",")