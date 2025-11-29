"""
main.py — CSS Analyzer entry point
──────────────────────────────────────────────
Pipeline:
1. Load CSS files directly from TARGET_URL
2. Merge remote CSS into combined.css
3. Parse CSS using cssutils + tinycss2
4. Build file → selector → property graph
5. (Optional) Map HTML usage
6. Write D3 visualization (HTML + assets)
7. (Optional) Run Ollama analysis
8. Serve interactive graph UI on port 8080
"""

import json
from pathlib import Path
from collections import Counter

from .config import settings



from .loader import load_css_remote
css_files = load_css_remote()





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

    prop_counter = Counter(l["target"] for l in links if l["type"] == "uses")

    summary = {
        "selectors": len(selectors),
        "properties": len(properties),
        "avg_declarations_per_selector": round(
            sum(n.get("decl_count", 0) for n in selectors)
            / max(len(selectors), 1),
            2
        ),
        "most_used_property": prop_counter.most_common(1)[0]
        if prop_counter else None,
        "total_links": len(links),
    }

    out = output_dir / "css_summary.json"
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

    # 2️⃣ Load CSS from TARGET_URL
    css_files = load_css_remote()     # <-- NEW SIGNATURE (no args)
    print(f"📂 Loaded {len(css_files)} remote CSS files.")

    if not css_files:
        print("⚠️ No CSS files found — exiting.")
        return

    # 3️⃣ Combine all CSS (already written by load_css, but we need it in memory)
    combined_css = "\n".join(
        f"/* ===== {name} ===== */\n{content}"
        for name, content in css_files.items()
    )
    combined_path = output_dir / "combined.css"
    combined_path.write_text(combined_css, encoding="utf-8")
    print(f"🧵 Combined CSS written → combined.css ({len(combined_css)} chars)")

    # 📄 Write combined lines (for frontend regex table)
    combined_lines = [
        {"num": i + 1, "text": line}
        for i, line in enumerate(combined_css.splitlines())
    ]
    (output_dir / "combined.lines.json").write_text(
        json.dumps({"lines": combined_lines}, indent=2),
        encoding="utf-8"
    )

    # 4️⃣ Parse CSS
    cssutils_rules = parse_with_cssutils(combined_css)
    tinycss_rules = parse_with_tinycss2(combined_css)
    print(f"🔍 Parsed {len(cssutils_rules)} cssutils rules, {len(tinycss_rules)} tinycss2 rules")

    # 5️⃣ Build graph
    graph = build_css_graph(css_files, cssutils_rules, tinycss_rules)
    graph_path = output_dir / "css_graph.json"
    graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(
        f"🗺  Graph JSON written → {graph_path.name} "
        f"({len(graph['nodes'])} nodes, {len(graph['links'])} links)"
    )

    # 6️⃣ Write visualization HTML
    html_path = output_dir / "css_graph.html"
    write_d3_html(html_path)
    print(f"📊 Visualization HTML written → {html_path.name}")

    # 7️⃣ Ollama-powered analysis (optional)
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

    # 9️⃣ Summary metrics
    summarize_css(graph, output_dir)

    # 🔟 Launch local web server
    print("\n🌐 Launching local visualization server at http://localhost:8080")
    serve_visualization(output_dir, port=8080)


if __name__ == "__main__":
    main()