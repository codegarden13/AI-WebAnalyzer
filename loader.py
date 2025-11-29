# loader.py — remote CSS loader
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict
from pathlib import Path
from .config import settings


def load_css_remote() -> Dict[str, str]:
    """Load all CSS files referenced in the target webpage HTML."""
    if not settings.TARGET_URL:
        raise ValueError("TARGET_URL must be set in .env for remote CSS mode.")

    print(f"🌍 Loading webpage HTML: {settings.TARGET_URL}")
    resp = requests.get(settings.TARGET_URL, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # -------------------------------------------------
    # 1) Extract <link rel="stylesheet" href="...">
    # -------------------------------------------------
    css_urls = []

    for link in soup.find_all("link"):
        rel = link.get("rel", [])
        href = link.get("href")

        if not href:
            continue

        # Accept any stylesheet-ish link
        if "stylesheet" in rel or href.lower().endswith(".css"):
            full_url = urljoin(settings.TARGET_URL, href)
            css_urls.append(full_url)

    css_urls = list(dict.fromkeys(css_urls))
    print(f"🔗 Found {len(css_urls)} CSS files in HTML.")

    # -------------------------------------------------
    # 2) Fetch each CSS file
    # -------------------------------------------------
    css_map: Dict[str, str] = {}
    for url in css_urls:
        try:
            print(f"📥 Fetching: {url}")
            text = requests.get(url, timeout=10).text
            fname = url.split("/")[-1]
            css_map[fname] = text
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")

    # -------------------------------------------------
    # 3) Write combined.css to output
    # -------------------------------------------------
    combined_path = Path(settings.OUTPUT_DIR) / "combined.css"
    combined_path.parent.mkdir(parents=True, exist_ok=True)

    combined_text = "\n".join(
        f"/* ===== {name} ===== */\n{text}" for name, text in css_map.items()
    )
    combined_path.write_text(combined_text, encoding="utf-8")

    print(f"🧵 combined.css written → {combined_path}")

    return css_map