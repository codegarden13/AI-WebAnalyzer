"""
main.py — CSS Analyzer entry point
──────────────────────────────────────────────
Combines:
- CSS file loading + merging
- CSS parsing (cssutils, tinycss2)
- Graph building + visualization
- Optional Ollama-based CSS refactor, audit, and graph reasoning
- Optional HTML mapping via TARGET_URL
- Summary metrics generation

All outputs are written into settings.OUTPUT_DIR
"""

import json
from pathlib import Path
from collections import Counter

from .config import settings
from .loader import load_css_files, combine_css
from .parser_css import parse_with_cssutils, parse_with_tinycss2
from .graph_builder import build_css_graph
from .visualizer import write_d3_html, serve_visualization
from .html_mapper import map_html_to_css

# Ollama modules
from .ollama.service import start_ollama, stop_ollama
from .ollama.audit import audit_css
from .ollama.graph_analysis import analyze_graph
from .ollama.refactor import refactor_css_files


# ───────────────────────────────────────────────
# Summary helper
# ───────────────────────────────────────────────
def summarize_css(graph, output_dir: Path):
    """Create a small summary report of CSS metrics."""
    selectors = [n for n in graph["nodes"] if n["type"] == "selector"]
    properties = [n for n in graph["nodes"] if n["type"] == "property"]
    links = graph["links"]

    if not selectors or not properties:
        print("⚠️ No selectors/properties found — skipping summary.")
        return

    prop_counter = Counter(l["target"] for l in links if l["type"] == "uses")

    summary = {
        "selectors": len(selectors),
        "properties": len(properties),
        "avg_declarations_per_selector": round(
            sum(n.get("decl_count", 0) for n in selectors) / max(len(selectors), 1), 2
        ),
        "most_used_property": prop_counter.most_common(1)[0] if prop_counter else None,
        "total_links": len(links),
    }

    out = Path(output_dir) / "css_summary.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"📈 Wrote summary metrics → {out.name}")


# ───────────────────────────────────────────────
# Main process
# ───────────────────────────────────────────────
def main():
    print("\n🎨 CSS Analyzer starting...\n")

    # 1️⃣ Prepare output directory
    output_dir = Path(settings.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir.resolve()}")

    # 2️⃣ Load CSS files
    css_files = load_css_files(settings.CSS_DIR, settings.CSS_ORDER_RAW)
    print(f"📂 Loaded {len(css_files)} CSS files from {settings.CSS_DIR}")

    if not css_files:
        print("⚠️ No CSS files found — exiting.")
        return

    # 3️⃣ Combine all CSS
    combined_css = combine_css(css_files)
    combined_path = output_dir / "combined.css"
    combined_path.write_text(combined_css, encoding="utf-8")
    print(f"🧵 Combined CSS written → {combined_path.name} ({len(combined_css)} chars)")

    # 4️⃣ Parse CSS
    cssutils_rules = parse_with_cssutils(combined_css)
    tinycss_rules = parse_with_tinycss2(combined_css)
    print(f"🔍 Parsed {len(cssutils_rules)} cssutils rules, {len(tinycss_rules)} tinycss2 rules")

    # 5️⃣ Build graph
    graph = build_css_graph(css_files, cssutils_rules, tinycss_rules)
    graph_path = output_dir / "css_graph.json"
    graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"🗺  Graph JSON written → {graph_path.name} "
          f"({len(graph['nodes'])} nodes, {len(graph['links'])} links)")

    # 6️⃣ Visualization template
    html_path = output_dir / "css_graph.html"
    write_d3_html(html_path)
    print(f"📊 Visualization HTML written → {html_path.name}")

    # 7️⃣ Ollama-powered steps (optional)
    if settings.USE_REFACTOR or settings.USE_AUDIT or settings.USE_GRAPH_ANALYSIS:
        print("\n🤖 Starting Ollama backend...")
        start_ollama()

        if settings.USE_REFACTOR:
            print("🧩 Running CSS refactor...")
            refactor_css_files(css_files, combined_css, output_dir)
        else:
            print("⚙️ Skipping refactor (USE_REFACTOR=false)")

        if settings.USE_AUDIT:
            print("📋 Running CSS audit...")
            audit_result = audit_css(css_files, combined_css)
            audit_path = output_dir / "css_audit.md"
            audit_path.write_text(audit_result, encoding="utf-8")
            print(f"🧾 Audit written → {audit_path.name}")
        else:
            print("⚙️ Skipping audit (USE_AUDIT=false)")

        if settings.USE_GRAPH_ANALYSIS:
            print("🧠 Running CSS graph analysis...")
            graph_result = analyze_graph(graph_path, combined_path)
            if "error" in graph_result:
                print(f"⚠️ Graph analysis error: {graph_result['error']}")
            else:
                graph_analysis_path = output_dir / "css_graph_analysis.md"
                graph_analysis_path.write_text(graph_result["markdown"], encoding="utf-8")
                print(f"🧭 Graph insights written → {graph_analysis_path.name}")
        else:
            print("⚙️ Skipping graph analysis (USE_GRAPH_ANALYSIS=false)")

        stop_ollama()
    else:
        print("\n⚙️ All Ollama features disabled — skipping AI analysis.")

    # 8️⃣ HTML mapping (optional)
    if settings.TARGET_URL:
        print(f"\n🌐 Mapping HTML from → {settings.TARGET_URL}")
        html_graph_path = output_dir / "css_graph_with_html.json"
        map_html_to_css(settings.TARGET_URL, graph_path, html_graph_path)
        print(f"✅ HTML mapping graph written → {html_graph_path.name}")
    else:
        print("⚙️ No TARGET_URL defined — skipping HTML mapping.")

    # 9️⃣ Write summary metrics
    summarize_css(graph, output_dir)

    # 🔟 Launch visualization (blocking)
    print("\n🌐 Launching local visualization server...")
    serve_visualization(output_dir, port=8080)


if __name__ == "__main__":
    main()