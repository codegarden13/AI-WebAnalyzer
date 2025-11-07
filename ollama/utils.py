import cssutils
cssutils.log.setLevel("FATAL")


import json

def safe_json_response(resp):
    """
    Parse Ollama's sometimes concatenated JSON responses safely.
    Returns the first valid JSON object.
    """
    try:
        return resp.json()
    except json.JSONDecodeError:
        text = resp.text.strip()
        if "\n" in text:
            # try to split multiple JSON objects
            parts = text.splitlines()
            for part in parts:
                try:
                    return json.loads(part)
                except Exception:
                    continue
        # last resort: try first brace block
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except Exception:
                pass
        return {"error": f"Invalid JSON response: {text[:200]}"}






def sanitize_css(result: str) -> str:
    """Validate model output and clean non-CSS lines."""
    try:
        cssutils.parseString(result)
        return result
    except Exception:
        valid_lines = [
            l for l in result.splitlines()
            if "{" in l or "}" in l or ":" in l
        ]
        return "\n".join(valid_lines)