import json
import time
import requests
from textwrap import dedent
from ..config import settings
from .service import start_ollama
from .utils import safe_json_response

MODEL = settings.OLLAMA_MODEL
BASE_URL = settings.OLLAMA_URL.rstrip("/")
API_GENERATE = f"{BASE_URL}/api/generate"
CHAR_LIMIT = getattr(settings, "CHAR_LIMIT", 30000)


def analyze_graph(graph_path, combined_path) -> dict:
    """
    Analyze the dependency graph and combined CSS.
    Uses Ollama to produce a high-level architectural analysis of selectors, files, and properties.

    Returns:
        {
            "markdown": <analysis_text>,
            "timestamp": <unix_timestamp>,
            "model": <model_name>,
        }
        or
        {
            "error": <error_message>
        }
    """
    print("🧩 Running graph-aware CSS analysis...")
    start_ollama()

    # --- Load graph + CSS safely
    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            graph = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load graph file '{graph_path}': {e}"}

    try:
        with open(combined_path, "r", encoding="utf-8") as f:
            css = f.read()[:CHAR_LIMIT]
    except Exception as e:
        return {"error": f"Failed to load combined CSS '{combined_path}': {e}"}

    # --- Build prompt for the model
    prompt = dedent(f"""
    You are a senior CSS systems architect.
    Using the following CSS and dependency graph data, perform a detailed analysis.

    Tasks:
    - Identify overly complex or over-connected selectors
    - Find unused or redundant properties
    - Detect high coupling between files
    - Recommend modular grouping (base, layout, components, utilities, theme)
    - Suggest specific restructuring steps to improve maintainability
    - Summarize in Markdown format (sections, bullet points, clarity)

    ### Combined CSS (truncated)
    ```css
    {css}
    ```

    ### Graph (truncated JSON)
    ```json
    {json.dumps(graph)[:5000]}
    ```
    """)

    # --- Send request
    print(f"🌐 Sending graph analysis request to: {API_GENERATE}")
    try:
        r = requests.post(
            API_GENERATE,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=300,
        )
    except requests.exceptions.ConnectionError as e:
        return {"error": f"Connection error while contacting Ollama ({API_GENERATE}): {e}"}
    except Exception as e:
        return {"error": f"Unexpected error during graph analysis: {e}"}

    # --- Validate response
    if r.status_code != 200:
        return {"error": f"Ollama returned {r.status_code}: {r.text[:200]}"}

    data = safe_json_response(r)
    if "error" in data:
        return {"error": f"Invalid JSON from Ollama: {data['error']}"}

    result = (data.get("response") or "").strip()
    if not result:
        return {"error": "Empty response from Ollama."}

    print("✅ Graph analysis completed successfully.")
    return {
        "markdown": result,
        "timestamp": time.time(),
        "model": MODEL,
    }