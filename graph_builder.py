"""
graph_builder.py
──────────────────────────────────────────────
Builds an enriched graph representation of CSS:
- selector → property relationships
- origin file name per selector
- declaration / usage / complexity metrics
- marks unused selectors
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
    Build a graph of CSS relationships (selector → property),
    enriched with declaration/usage metrics, specificity, and file origin.
    """
    nodes, links = [], []
    selector_set, prop_set = set(), set()

    # ───────────────────────────────
    # 1️⃣ Build selector and property nodes
    # ───────────────────────────────
    for rule in cssutils_rules:
        if rule.get("type") != "style":
            continue

        selector = rule.get("selector")
        if not selector:
            continue

        # Determine origin file (based on match in css_files)
        file_origin = _find_file_for_selector(css_files, selector)

        # Add selector node (once)
        if selector not in selector_set:
            selector_set.add(selector)
            node = {
                "id": f"sel::{selector}",
                "type": "selector",
                "label": selector,
                "file": file_origin,
                "specificity": _estimate_specificity(selector),
                "complexity": _estimate_complexity(selector),
                "length": len(selector),
                "has_id": "#" in selector,
                "has_class": "." in selector,
                "combinators": len(re.findall(r"[ >+~]", selector)),
                "css_text": rule.get("text", "").strip()[:300],  # keep short preview
                "unused": False,  # will be marked true later by HTML mapping
            }
            nodes.append(node)

        # Add property nodes + "uses" links
        for decl in rule.get("declarations", []):
            prop = decl.get("property")
            if not prop:
                continue

            if prop not in prop_set:
                prop_set.add(prop)
                nodes.append({
                    "id": f"prop::{prop}",
                    "type": "property",
                    "label": prop,
                })

            links.append({
                "source": f"sel::{selector}",
                "target": f"prop::{prop}",
                "type": "uses",
            })

    # ───────────────────────────────
    # 2️⃣ Compute per-node metrics
    # ───────────────────────────────
    for node in nodes:
        if node["type"] == "selector":
            decl_count = sum(
                1 for l in links if l["source"] == node["id"] and l["type"] == "uses"
            )
            node["decl_count"] = decl_count
            node["score"] = node["complexity"] + node["specificity"] + decl_count
        elif node["type"] == "property":
            usage_count = sum(
                1 for l in links if l["target"] == node["id"] and l["type"] == "uses"
            )
            node["usage_count"] = usage_count

    # ───────────────────────────────
    # 3️⃣ Graph metadata
    # ───────────────────────────────
    meta = {
        "generated": datetime.datetime.utcnow().isoformat() + "Z",
        "files": len(css_files),
        "selectors": len(selector_set),
        "properties": len(prop_set),
        "total_links": len(links),
        "avg_complexity": round(
            sum(n.get("complexity", 0) for n in nodes if n["type"] == "selector")
            / (len(selector_set) or 1),
            2,
        ),
        "avg_specificity": round(
            sum(n.get("specificity", 0) for n in nodes if n["type"] == "selector")
            / (len(selector_set) or 1),
            2,
        ),
    }

    return {"meta": meta, "nodes": nodes, "links": links}


# ───────────────────────────────
# 🔍 Helper functions
# ───────────────────────────────

def _find_file_for_selector(css_files: Dict[str, str], selector: str) -> str:
    """Return filename that most likely defines this selector."""
    for f, text in css_files.items():
        if selector in text:
            return f
    return "unknown"


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