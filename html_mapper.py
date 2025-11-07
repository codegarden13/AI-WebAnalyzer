"""
html_mapper.py
──────────────────────────────────────────────
Fetches HTML (local or remote), parses the DOM structure,
and links HTML elements to CSS selectors from the existing CSS graph.

Adds:
- HTML nodes (type="html")
- 'matches' links (html → selector)
- Marks unused CSS selectors with `unused: true`

Outputs:
- Extended graph JSON
- Summary dictionary (counts, unused selectors)
"""

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path
import re


def map_html_to_css(url: str, css_graph_path: str, output_path: str, limit: int = 500):
    """
    Fetch HTML and map DOM elements to CSS selectors.

    Args:
        url (str): Target URL or local HTML file path.
        css_graph_path (str): Path to existing CSS graph JSON.
        output_path (str): Output path for the extended graph file.
        limit (int): Max number of HTML nodes to include (default 500).

    Returns:
        dict: Summary with node/link counts and unused selectors.
    """
    print(f"🌐 Fetching HTML from: {url}")

    # ───────────────────────────────
    # 1️⃣ Load HTML content
    # ───────────────────────────────
    html = ""
    try:
        if url.startswith(("http://", "https://")):
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            html = resp.text
        else:
            html = Path(url).read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Failed to load HTML from {url}: {e}")
        return {"error": str(e)}

    soup = BeautifulSoup(html, "html.parser")

    # ───────────────────────────────
    # 2️⃣ Collect DOM nodes
    # ───────────────────────────────
    dom_nodes = []
    for tag in soup.find_all(True):  # all tags
        node = {
            "tag": tag.name,
            "id": tag.get("id"),
            "classes": tag.get("class", []),
        }
        dom_nodes.append(node)

    print(f"🧩 Parsed {len(dom_nodes)} HTML elements from DOM.")

    # ───────────────────────────────
    # 3️⃣ Load CSS graph
    # ───────────────────────────────
    try:
        with open(css_graph_path, "r", encoding="utf-8") as f:
            css_graph = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read CSS graph file: {e}")
        return {"error": str(e)}

    css_selectors = [n for n in css_graph["nodes"] if n["type"] == "selector"]

    new_nodes, new_links = [], []
    matched_selectors = set()

    # ───────────────────────────────
    # 4️⃣ Add HTML nodes
    # ───────────────────────────────
    for i, node in enumerate(dom_nodes[:limit]):
        label_parts = [f"<{node['tag']}>"]
        if node["id"]:
            label_parts.append(f"#{node['id']}")
        if node["classes"]:
            label_parts.append("." + ".".join(node["classes"]))
        label = "".join(label_parts)

        new_nodes.append({
            "id": f"html::{i}",
            "type": "html",
            "label": label,
            "group": 4,
        })

    # ───────────────────────────────
    # 5️⃣ Match HTML nodes ↔ CSS selectors
    # ───────────────────────────────
    for html_node in new_nodes:
        label = html_node["label"].lower()
        tag_match = re.search(r"<(\w+)>", label)
        tag = tag_match.group(1) if tag_match else None
        ids = re.findall(r"#([\w\-_]+)", label)
        classes = re.findall(r"\.([\w\-_]+)", label)

        for css_node in css_selectors:
            selector = css_node["label"].strip().lower()

            # Basic direct matching rules
            matches = False
            if tag and selector == tag:
                matches = True
            if any(f"#{i}" in selector for i in ids):
                matches = True
            if any(f".{c}" in selector for c in classes):
                matches = True
            if tag and any(f"{tag}." in selector for c in classes):
                matches = True

            # Skip pseudo-classes/pseudo-elements for matching
            selector_clean = re.sub(r":[\w\-()]+", "", selector)
            if selector_clean and tag and selector_clean == tag:
                matches = True

            if matches:
                new_links.append({
                    "source": html_node["id"],
                    "target": css_node["id"],
                    "type": "matches",
                })
                matched_selectors.add(css_node["id"])

    # ───────────────────────────────
    # 6️⃣ Mark unused selectors
    # ───────────────────────────────
    all_selector_ids = {n["id"] for n in css_selectors}
    unused_selectors = all_selector_ids - matched_selectors
    for sel in css_selectors:
        sel["unused"] = sel["id"] in unused_selectors

    print(f"🔍 Found {len(unused_selectors)} unused CSS selectors.")

    # ───────────────────────────────
    # 7️⃣ Extend CSS graph
    # ───────────────────────────────
    css_graph["nodes"].extend(new_nodes)
    css_graph["links"].extend(new_links)

    # Add meta summary
    css_graph.setdefault("meta", {})
    css_graph["meta"]["html_nodes"] = len(new_nodes)
    css_graph["meta"]["matches_links"] = len(new_links)
    css_graph["meta"]["unused_selectors"] = len(unused_selectors)

    # ───────────────────────────────
    # 8️⃣ Save output
    # ───────────────────────────────
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(css_graph, f, indent=2)

    print(f"✅ Extended graph with HTML mapping → {output_path}")
    print(f"🔗 Added {len(new_nodes)} HTML nodes and {len(new_links)} 'matches' links.")

    return {
        "html_nodes": len(new_nodes),
        "matches_links": len(new_links),
        "unused_selectors": sorted(list(unused_selectors)),
        "output": str(output_path),
    }