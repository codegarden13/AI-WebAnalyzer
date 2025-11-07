"""
ollama_client.py
──────────────────────────────────────────────
Single, cleaned-up Ollama client for your css-analyzer-ollama project.

Features
- always tries to START Ollama (via Homebrew on macOS)
- waits until the API is ready (http://localhost:11434/api/tags)
- provides 3 high-level calls:
    1) ask_ollama_for_css_refactor(...)     → returns cleaned CSS
    2) ask_ollama_for_css_audit(...)        → returns markdown audit
    3) ask_ollama_for_graph_analysis(...)   → returns markdown (graph-based insights)
- writes meaningful error messages incl. the URL that failed
- avoids circular imports (no self-imports)
- stops Ollama again — but **only if this module started it**

NOTE:
- this client expects .env / config.py to provide:
    - settings.OLLAMA_URL  (e.g. "http://localhost:11434")
    - settings.OLLAMA_MODEL (e.g. "mistral:7b")
    - settings.CHAR_LIMIT   (e.g. 30000)
"""

import json
import time
import platform
import shutil
import subprocess
from textwrap import dedent
from typing import Dict, Any

import requests
import cssutils

from .config import settings


# ─────────────────────────────────────────────
# GLOBAL SETTINGS / CONSTANTS
# ─────────────────────────────────────────────
BASE_URL = settings.OLLAMA_URL.rstrip("/")  # e.g. http://localhost:11434
API_TAGS = f"{BASE_URL}/api/tags"
API_GENERATE = f"{BASE_URL}/api/generate"
MODEL_NAME = settings.OLLAMA_MODEL
CHAR_LIMIT = getattr(settings, "CHAR_LIMIT", 30000)

# we track whether THIS module started ollama
_STARTED_HERE = False


# ─────────────────────────────────────────────
# LOW-LEVEL SERVICE CONTROL
# ─────────────────────────────────────────────
def is_ollama_running() -> bool:
    """Return True if the Ollama API is responding."""
    try:
        resp = requests.get(API_TAGS, timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def start_ollama() -> bool:
    """
    Ensure Ollama is running.
    - If it's already running: just return True.
    - Else: try to start via `brew services start ollama` (macOS).
    - Wait up to ~120s.
    """
    global _STARTED_HERE

    print("🚀 Ensuring Ollama service is running...")

    # already running
    if is_ollama_running():
        print("✅ Ollama is already running.")
        return True

    # try to start via brew (macOS)
    if shutil.which("brew") and platform.system() == "Darwin":
        print("🔧 Starting Ollama via Homebrew...")
        subprocess.run(["brew", "services", "start", "ollama"], check=False)
    else:
        print("⚠️ No Homebrew detected or not macOS. "
              "Please start Ollama manually in another terminal: `ollama serve`")

    # wait until ready
    for i in range(60):  # 60 × 2s = 120s
        if is_ollama_running():
            print("✅ Ollama is ready.")
            _STARTED_HERE = True
            return True
        time.sleep(2)
        if i % 10 == 0:
            print("⏳ Waiting for Ollama to start...")

    print(f"❌ Ollama did not respond at {API_TAGS} — continuing, "
          "but requests will likely fail.")
    return False


def stop_ollama() -> None:
    """
    Stop Ollama **only** if this module started it.
    That way we don't kill a user’s global Ollama daemon.
    """
    global _STARTED_HERE

    if not _STARTED_HERE:
        # someone else runs ollama — leave it alone
        print("🟡 Not stopping Ollama (it was not started by this script).")
        return

    print("🛑 Stopping Ollama service...")
    if shutil.which("brew") and platform.system() == "Darwin":
        subprocess.run(["brew", "services", "stop", "ollama"], check=False)
        print("✅ Ollama stopped.")
    else:
        print("⚠️ Could not stop via brew — please stop Ollama manually.")
    _STARTED_HERE = False


# ─────────────────────────────────────────────
# HELPER: CLEAN / VALIDATE CSS
# ─────────────────────────────────────────────
def _sanitize_ollama_css(result: str) -> str:
    """
    Try to parse the model output as CSS.
    If it fails, keep only lines that look like CSS rules/declarations.
    """
    cssutils.log.setLevel("FATAL")
    try:
        cssutils.parseString(result)
        return result
    except Exception:
        print("⚠️ Ollama returned invalid CSS. Trimming suspicious lines.")
        valid_lines = [
            line for line in result.splitlines()
            if "{" in line or "}" in line or ":" in line
        ]
        return "\n".join(valid_lines)


# ─────────────────────────────────────────────
# 1) CSS REFACTOR
# ─────────────────────────────────────────────
def ask_ollama_for_css_refactor(css_text: str) -> str:
    """
    Always tries to refactor the provided CSS.
    If Ollama is not available, returns a CSS comment with the error.
    """
    start_ollama()

    truncated = css_text[:CHAR_LIMIT]
    print(f"🤖 Refactor: sending {len(truncated)} chars to Ollama ({MODEL_NAME})")
    endpoint = API_GENERATE
    print(f"🌐 Refactor request URL: {endpoint}")

    prompt = dedent(f"""
    You are a senior frontend architect and CSS refactoring expert.

    Refactor and simplify the following CSS while preserving ALL visual behavior.

    Rules:
    - merge duplicate selectors and declarations
    - group related declarations
    - convert repeated values (colors, spacing) to :root custom properties
    - keep selector names and specificity the same
    - output ONLY valid CSS — no markdown, no prose, no comments

    CSS input:
    ```css
    {truncated}
    ```
    """)

    for attempt in range(2):
        try:
            resp = requests.post(
                endpoint,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=180,
            )
            if resp.status_code != 200:
                # include the URL in error
                return f"/* Ollama error {resp.status_code} ({endpoint}): {resp.text[:200]} */"

            result = (resp.json().get("response") or "").strip()
            if not result:
                return f"/* ⚠️ Empty refactor response from Ollama ({endpoint}) */"

            # handle ```css ... ``` wrappers
            if "```" in result:
                cleaned = []
                inside = False
                for line in result.splitlines():
                    if line.strip().startswith("```"):
                        inside = not inside
                        continue
                    if inside or "{" in line or ":" in line:
                        cleaned.append(line)
                result = "\n".join(cleaned).strip()

            result = _sanitize_ollama_css(result)

            if len(result) < 20 and attempt == 0:
                print("⚠️ Refactor output looks too short — retrying once...")
                time.sleep(1.5)
                continue

            print("✅ CSS refactor completed.")
            return result

        except requests.exceptions.ConnectionError as e:
            return f"/* ❌ Connection error to Ollama ({endpoint}): {e} */"
        except Exception as e:
            if attempt == 0:
                print(f"⚠️ Error on attempt 1: {e} — retrying...")
                time.sleep(1.5)
                continue
            return f"/* ❌ Ollama request failed ({endpoint}): {e} */"

    return "/* ❌ Ollama failed to produce usable CSS after 2 attempts */"


# ─────────────────────────────────────────────
# 2) CSS AUDIT (structure, layering, duplicates)
# ─────────────────────────────────────────────
def ask_ollama_for_css_audit(css_files: Dict[str, str], combined_css: str) -> str:
    """
    Ask Ollama for a human-readable, structured CSS audit:
    - redundancies
    - suggested file structure
    - tokens/variables
    - naming/layering conventions
    """
    start_ollama()

    # keep each file short to fit into context
    per_file_max = 2800
    file_blocks = []
    for name, content in css_files.items():
        file_blocks.append(
            f"### {name}\n```css\n{content[:per_file_max]}\n```"
        )

    combined_trunc = combined_css[:CHAR_LIMIT]
    endpoint = API_GENERATE
    print(f"🌐 Audit request URL: {endpoint}")

    prompt = dedent(f"""
    You are a senior frontend architect performing a CSS audit.

    You get:
    1. A combined CSS build (all styles merged)
    2. Individual CSS files (possibly overlapping)

    Your task:
    - detect overlapping or redundant selectors
    - detect repeated color / spacing / typography values
    - propose :root variables for those
    - propose a cleaner CSS file structure (base, layout, components, utilities, theme)
    - point out legacy / too-specific selectors
    - suggest how to reduce specificity and improve maintainability
    - return the answer in Markdown with sections

    ## Combined CSS (truncated)
    ```css
    {combined_trunc}
    ```

    ## Individual files (truncated)
    {chr(10).join(file_blocks[:10])}
    """)

    try:
        resp = requests.post(
            endpoint,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=240,
        )
        if resp.status_code != 200:
            return f"⚠️ Ollama audit error {resp.status_code} ({endpoint}): {resp.text[:200]}"

        result = resp.json().get("response", "").strip()
        if not result:
            return "⚠️ Ollama returned no audit text."
        print("✅ CSS audit completed.")
        return result

    except Exception as e:
        return f"⚠️ Ollama CSS audit failed ({endpoint}): {e}"


# ─────────────────────────────────────────────
# 3) GRAPH-AWARE ANALYSIS (uses css_graph.json)
# ─────────────────────────────────────────────
def ask_ollama_for_graph_analysis(graph_path, combined_css_path) -> Dict[str, Any]:
    """
    Ask Ollama to analyze the CSS dependency graph (files → selectors → properties)
    together with the combined CSS. Returns a dict:
        {
          "markdown": "...",
          "timestamp": ...,
          "model": "...",
        }
    or { "error": "..." }
    """
    start_ollama()
    print("🧩 Running graph-aware CSS analysis...")

    # load graph
    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
    except Exception as e:
        return {"error": f"Failed to read CSS graph ({graph_path}): {e}"}

    with open(combined_css_path, "r", encoding="utf-8") as f:
        combined_css = f.read()[:CHAR_LIMIT]

    endpoint = API_GENERATE
    print(f"🌐 Graph analysis request URL: {endpoint}")

    # keep graph small so LLM survives
    graph_snippet = json.dumps(graph_data)[:5000]

    prompt = dedent(f"""
    You are a senior frontend architect analyzing a CSS dependency graph.

    You are given:
    - a combined CSS build
    - a JSON graph with nodes (files, selectors, properties) and links (defines, uses)

    Tasks:
    - describe the overall CSS structure (which files / selectors are central)
    - find over-connected selectors or "god components"
    - find overused properties (used by many selectors)
    - propose a better modularization: base, layout, components, utilities, theme
    - show which selectors should be extracted into utilities
    - show which files are too tightly coupled
    - output actionable next steps for refactoring

    ### Combined CSS (truncated)
    ```css
    {combined_css}
    ```

    ### CSS Graph (truncated JSON)
    ```json
    {graph_snippet}
    ```
    """)

    try:
        resp = requests.post(
            endpoint,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )
        if resp.status_code != 200:
            return {
                "error": f"Ollama graph analysis error {resp.status_code} "
                         f"({endpoint}): {resp.text[:200]}"
            }

        result = resp.json().get("response", "").strip()
        if not result:
            return {"error": "Ollama returned empty graph analysis."}

        print("✅ Graph-aware CSS analysis completed.")
        return {
            "markdown": result,
            "timestamp": time.time(),
            "model": MODEL_NAME,
        }

    except Exception as e:
        return {"error": f"Ollama graph analysis failed ({endpoint}): {e}"}
    finally:
        # do NOT always stop here — main.py can decide.
        # If you want auto-stop here, uncomment:
        # stop_ollama()
        ...