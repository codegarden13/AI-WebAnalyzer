"""
html_mapper.py
──────────────────────────────────────────────
Maps HTML DOM to existing CSS selectors — *without*
adding HTML nodes or links.

This module:
- Fetches HTML (remote or local)
- Checks which CSS selectors match elements in the DOM
- Marks nodes: unused = True / False
- Writes a clean, enriched CSS graph

No HTML nodes, no match-links are created.
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path


def map_html_to_css(url: str, css_graph_path: str, output_path: str):
    """
    Mark which selectors are used in the HTML document.
    NO nodes or links are added.

    Args:
        url (str): URL or path to HTML file
        css_graph_path (str): Input CSS graph JSON
        output_path (str): Output CSS graph JSON
    """

    print(f"🌐 Fetching HTML from: {url}")

    # -------------------------------------------------
    # 1) Load HTML content
    # -------------------------------------------------
    try:
        if url.startswith(("http://", "https://")):
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            html = resp.text
        else:
            html = Path(url).read_text(encoding="utf-8")

    except Exception as e:
        print(f"❌ Failed to load HTML: {e}")
        return {"error": str(e)}

    soup = BeautifulSoup(html, "html.parser")

    # -------------------------------------------------
    # 2) Load CSS graph
    # -------------------------------------------------
    try:
        graph = json.loads(Path(css_graph_path).read_text())
    except Exception as e:
        print(f"❌ Failed to load CSS graph: {e}")
        return {"error": str(e)}

    selector_nodes = [n for n in graph["nodes"] if n["type"] == "selector"]

    print(f"📊 Checking {len(selector_nodes)} selectors in HTML...")

    used = set()

    # -------------------------------------------------
    # 3) Test all selectors via soup.select()
    # -------------------------------------------------
    for node in selector_nodes:
        selector = node["label"]

        try:
            matches = soup.select(selector)
            if matches:
                used.add(node["id"])
        except Exception:
            # Invalid selector (CSS4 pseudo etc.)
            pass

    # -------------------------------------------------
    # 4) Assign unused flags
    # -------------------------------------------------
    for node in selector_nodes:
        node["unused"] = node["id"] not in used

    unused_count = sum(1 for n in selector_nodes if n["unused"])

    print(f"🔍 Found {unused_count} unused selectors.")

    # -------------------------------------------------
    # 5) Write output graph
    # -------------------------------------------------
    graph.setdefault("meta", {})
    graph["meta"]["unused_selectors"] = unused_count
    graph["meta"]["used_selectors"] = len(used)

    Path(output_path).write_text(json.dumps(graph, indent=2), encoding="utf-8")

    print(f"✅ Updated graph written → {output_path}")

    return {
        "unused_selectors": unused_count,
        "used_selectors": len(used),
        "output": str(output_path),
    }