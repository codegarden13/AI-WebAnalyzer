from pathlib import Path
from typing import Dict, List

from pathlib import Path
from typing import Dict, List
from .config import settings

def load_css_files(css_dir: Path, css_order_raw: str) -> Dict[str, str]:
    """
    Returns dict {filename: content}.
    - If CSS_MODE='order': only use files from CSS_ORDER.
    - If CSS_MODE='all': order those first, then append remaining alphabetically.
    """
    files: Dict[str, str] = {}

    ordered_names: List[str] = []
    if css_order_raw:
        ordered_names = [p.strip() for p in css_order_raw.split(",") if p.strip()]

    all_css_files = {p.name: p for p in css_dir.glob("*.css")}

    if settings.CSS_MODE == "order":
        # ✅ Only use ordered files
        for name in ordered_names:
            p = all_css_files.get(name)
            if p and p.exists():
                files[name] = p.read_text(encoding="utf-8")
        missing = [n for n in ordered_names if n not in files]
        if missing:
            print(f"⚠️ Warning: Missing CSS files: {', '.join(missing)}")
        print(f"✅ Loaded {len(files)} CSS files in strict order mode.")
        return files

    # Default: include all (ordered first, then rest alphabetically)
    for name in ordered_names:
        p = all_css_files.pop(name, None)
        if p and p.exists():
            files[name] = p.read_text(encoding="utf-8")

    for name in sorted(all_css_files.keys()):
        p = all_css_files[name]
        files[name] = p.read_text(encoding="utf-8")

    print(f"✅ Loaded {len(files)} CSS files (ordered + all others).")
    return files

def combine_css(css_map: Dict[str, str]) -> str:
    return "\n".join(f"/* ===== {n} ===== */\n{c}" for n, c in css_map.items())