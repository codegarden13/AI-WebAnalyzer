"""
visualizer.py
──────────────────────────────
Handles the creation and serving of the D3 HTML visualization.
- Copies your HTML template into the output folder
- Starts a simple HTTP server for live preview
"""

import os
import shutil
import webbrowser
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from pathlib import Path

import os
import shutil
from pathlib import Path

def write_d3_html(output_path: Path):
    """Copy the D3 visualization template and assets to the output folder."""
    root = Path(__file__).parent
    template = root / "templates" / "css_graph.html"
    if not template.exists():
        raise FileNotFoundError(f"Template not found: {template}")

    # Copy template HTML
    shutil.copy(template, output_path)
    print(f"📄 Copied template → {output_path}")

    # Copy assets safely
    assets_src = root / "assets"
    assets_dst = output_path.parent / "assets"
    if assets_src.exists():
        for src_dir, _, files in os.walk(assets_src):
            rel_dir = Path(src_dir).relative_to(assets_src)
            dst_dir = assets_dst / rel_dir
            dst_dir.mkdir(parents=True, exist_ok=True)

            for f in files:
                src_file = Path(src_dir) / f
                dst_file = dst_dir / f
                if src_file.resolve() == dst_file.resolve():
                    print(f"⚠️ Skipping same file: {src_file}")
                    continue
                shutil.copy2(src_file, dst_file)
        print(f"📦 Assets copied → {assets_dst}")
def serve_visualization(output_dir: Path, port: int = 8080):
    """
    Serve the visualization folder and open it in the default browser.
    Runs in foreground until user stops (Ctrl+C).
    """
    output_dir = Path(output_dir).resolve()
    html_path = output_dir / "css_graph.html"
    url = f"http://localhost:{port}/{html_path.name}"

    if not html_path.exists():
        print(f"❌ {html_path.name} not found in {output_dir}")
        return

    os.chdir(output_dir)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return  # silence default request logs

    TCPServer.allow_reuse_address = True

    with TCPServer(("localhost", port), QuietHandler) as httpd:
        print(f"🌐 Serving {output_dir}")
        print(f"🚀 Visualization available at: {url}")
        webbrowser.open(url)
        print("💡 Press Ctrl+C to stop the server.\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user.")