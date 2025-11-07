import requests
import time
from pathlib import Path
from textwrap import dedent
from ..config import settings
from .service import start_ollama
from .utils import sanitize_css, safe_json_response

MODEL = settings.OLLAMA_MODEL
BASE_URL = settings.OLLAMA_URL.rstrip("/")
CHAR_LIMIT = getattr(settings, "CHAR_LIMIT", 30000)
API_GENERATE = f"{BASE_URL}/api/generate"


def refactor_css_files(css_files: dict, combined_css: str, output_dir: Path) -> str:
    """
    Refactor each CSS file individually, using the combined CSS as context.
    For each file, Ollama returns:
      1️⃣ A short summary (Markdown)
      2️⃣ Refactored CSS
    Both are saved in output/refactored/.
    Returns merged refactored CSS string.
    """
    start_ollama()
    refactored_dir = output_dir / "refactored"
    refactored_dir.mkdir(parents=True, exist_ok=True)

    combined_context = combined_css[:CHAR_LIMIT]
    merged_css_result = []
    merged_summaries = []

    print(f"🤖 Starting per-file CSS refactor for {len(css_files)} files...")

    for idx, (name, content) in enumerate(css_files.items(), start=1):
        snippet = content[:CHAR_LIMIT]
        print(f"🔧 Refactoring [{idx}/{len(css_files)}] → {name}")

        prompt = dedent(f"""
        You are a senior CSS architect.

        Context:
        - You have the complete combined CSS of the project.
        - You will refactor only this file: "{name}"

        Tasks:
        1. **Analyze** this file for structure, duplication, and variable use.
        2. **Summarize** what changes you will make and why (in clear Markdown).
        3. **Refactor** the CSS while preserving visual behavior.

        Output format (exactly this order):
        ```
        ### Summary
        <short markdown summary>

        ### Refactored CSS
        <pure CSS only>
        ```

        ### Combined CSS (context, truncated)
        ```css
        {combined_context}
        ```

        ### Current file ({name})
        ```css
        {snippet}
        ```
        """)

        try:
            r = requests.post(
                API_GENERATE,
                json={"model": MODEL, "prompt": prompt, "stream": False},
                timeout=240,
            )
        except requests.exceptions.ConnectionError as e:
            result_css = f"/* ❌ Connection error ({API_GENERATE}): {e} */"
            summary = f"⚠️ Could not connect to Ollama for {name}."
        except Exception as e:
            result_css = f"/* ❌ Request error: {e} */"
            summary = f"⚠️ Unexpected request error for {name}."
        else:
            if r.status_code != 200:
                result_css = f"/* ⚠️ Ollama error {r.status_code}: {r.text[:200]} */"
                summary = f"Ollama returned {r.status_code} for {name}."
            else:
                data = safe_json_response(r)
                if "error" in data:
                    result_css = f"/* ⚠️ Invalid JSON: {data['error']} */"
                    summary = f"Response for {name} could not be parsed."
                else:
                    response_text = (data.get("response") or "").strip()
                    # Split the summary and CSS
                    summary, result_css = _split_summary_and_css(response_text)
                    result_css = sanitize_css(result_css)

        # Write both files
        (refactored_dir / f"{name}.refactored.css").write_text(result_css, encoding="utf-8")
        (refactored_dir / f"{name}.summary.md").write_text(summary, encoding="utf-8")
        print(f"✅ Refactored → {name}")

        merged_css_result.append(f"/* {name} */\n{result_css}\n")
        merged_summaries.append(f"## {name}\n\n{summary.strip()}\n\n---\n")

        time.sleep(1)

    # Write combined outputs
    merged_css = "\n".join(merged_css_result)
    merged_summary = "\n".join(merged_summaries)
    (output_dir / "combined.refactored.css").write_text(merged_css, encoding="utf-8")
    (output_dir / "combined_refactor_summary.md").write_text(merged_summary, encoding="utf-8")

    print(f"✨ Combined refactored CSS written → combined.refactored.css")
    print(f"🧾 Combined refactor summary written → combined_refactor_summary.md")

    return merged_css


def _split_summary_and_css(text: str) -> tuple[str, str]:
    """
    Extracts '### Summary' and '### Refactored CSS' sections from model response.
    Returns (summary, css)
    """
    summary = ""
    css = ""
    current = None

    for line in text.splitlines():
        if "### Summary" in line:
            current = "summary"
            continue
        elif "### Refactored CSS" in line:
            current = "css"
            continue
        if current == "summary":
            summary += line + "\n"
        elif current == "css":
            css += line + "\n"

    # fallback if no headers detected
    if not css.strip():
        css = text
    if not summary.strip():
        summary = "No summary returned."
    return summary.strip(), css.strip()