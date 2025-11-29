"""
graph_builder.py
──────────────────────────────────────────────
Builds an enriched graph representation of CSS:

Nodes
- file        → each CSS file
- selector    → each CSS selector
- property    → each CSS property name

Links
- defines     → file → selector (where the selector is defined)
- uses        → selector → property

Each selector is enriched with:
- origin file name
- declaration count
- specificity / complexity
- basic flags (has_id, has_class, combinators, length)
- css_text preview
- unused flag (set later by html_mapper)

Graph is ready for D3 visualization and audits.
"""

import datetime
import re
from typing import Dict, Any, List


def build_css_graph(
    css_files: Dict[str, str],
    cssutils_rules: List[Dict[str, Any]],
    tinycss_rules: List[Dict[str, Any]],   # kept for future use / extension
) -> Dict[str, Any]:
    """
    Build a graph of CSS relationships:
      file → selector → property

    Enriched with:
      - declaration / usage metrics
      - specificity / complexity scores
      - origin file mapping per selector
    """
    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []

    selector_set = set()
    prop_set = set()
    file_ids = set()

    # ───────────────────────────────
    # 1️⃣ File nodes
    # ───────────────────────────────
    for filename in css_files.keys():
        file_id = f"file::{filename}"
        file_ids.add(file_id)
        nodes.append({
            "id": file_id,
            "type": "file",
            "label": filename,
        })

    # ───────────────────────────────
    # 2️⃣ Selector & property nodes
    #     + selector → property "uses" links
    #     + file → selector "defines" links
    # ───────────────────────────────
    for rule in cssutils_rules:
        if rule.get("type") != "style":
            continue

        selector = rule.get("selector")
        if not selector:
            continue

        # Find file where this selector most likely comes from
        file_origin = _find_file_for_selector(css_files, selector)
        file_id = f"file::{file_origin}" if file_origin != "unknown" else None

        # --- Selector node (once per selector string) ---
        if selector not in selector_set:
            selector_set.add(selector)

            selector_node = {
                "id": f"sel::{selector}",
                "type": "selector",
                "label": selector,
                "file": file_origin,  # e.g. "0_tokens.css"
                "specificity": _estimate_specificity(selector),
                "complexity": _estimate_complexity(selector),
                "length": len(selector),
                "has_id": "#" in selector,
                "has_class": "." in selector,
                "combinators": len(re.findall(r"[ >+~]", selector)),
                "css_text": rule.get("text", "").strip()[:300],  # short preview
                "unused": False,  # will later be set by html_mapper
            }
            nodes.append(selector_node)

        selector_id = f"sel::{selector}"

        # --- File → selector link (defines) ---
        if file_id and file_id in file_ids:
            links.append({
                "source": file_id,
                "target": selector_id,
                "type": "defines",
            })

        # --- Property nodes + selector → property links ---
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
                "source": selector_id,
                "target": f"prop::{prop}",
                "type": "uses",
            })

    # ───────────────────────────────
    # 3️⃣ Per-node metrics
    # ───────────────────────────────
    for node in nodes:
        if node["type"] == "selector":
            decl_count = sum(
                1 for l in links
                if l["source"] == node["id"] and l["type"] == "uses"
            )
            node["decl_count"] = decl_count
            node["score"] = (
                node.get("complexity", 0)
                + node.get("specificity", 0)
                + decl_count
            )

        elif node["type"] == "property":
            usage_count = sum(
                1 for l in links
                if l["target"] == node["id"] and l["type"] == "uses"
            )
            node["usage_count"] = usage_count

    # ───────────────────────────────
    # 4️⃣ Graph metadata
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

    return {
        "meta": meta,
        "nodes": nodes,
        "links": links,
    }


# ───────────────────────────────
# 🔍 Helper functions
# ───────────────────────────────

def _find_file_for_selector(css_files: Dict[str, str], selector: str) -> str:
    """
    Return filename that most likely defines this selector.

    Simple heuristic:
    - First file whose text contains the selector string.
    - If none, returns "unknown".
    """
    for filename, text in css_files.items():
        if selector in text:
            return filename
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