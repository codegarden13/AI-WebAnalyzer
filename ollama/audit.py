import requests
from textwrap import dedent
from ..config import settings
from .service import start_ollama
from .utils import safe_json_response

MODEL = settings.OLLAMA_MODEL
CHAR_LIMIT = settings.CHAR_LIMIT
API_GENERATE = settings.OLLAMA_URL.rstrip("/") + "/api/generate"

def audit_css(css_files: dict, combined: str) -> str:
    """Perform a CSS audit and return Markdown analysis."""
    start_ollama()
    snippet = combined[:CHAR_LIMIT]
    file_samples = "\n".join([
        f"### {n}\n```css\n{t[:2000]}\n```"
        for n, t in list(css_files.items())[:5]
    ])

    prompt = dedent(f"""
    You are a senior frontend architect.
    Analyze this CSS set and report in Markdown:
    - redundant selectors
    - duplicate values
    - possible variables
    - suggested structure (base/layout/components/theme)
    - naming improvements

    ### Combined CSS
    ```css
    {snippet}
    ```

    ### Individual files
    {file_samples}
    """)

    r = requests.post(API_GENERATE, json={"model": MODEL, "prompt": prompt, "stream": False})
    if r.status_code != 200:
        return f"⚠️ Error {r.status_code}: {r.text[:150]}"

    data = safe_json_response(r)
    if "error" in data:
        return f"⚠️ Ollama JSON parse error: {data['error']}"

    return (data.get("response") or "").strip()