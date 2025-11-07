import cssutils
import tinycss2
from typing import Dict, Any, List

def parse_with_cssutils(css_text: str) -> List[Dict[str, Any]]:
    cssutils.log.setLevel("FATAL")
    sheet = cssutils.parseString(css_text)
    rules = []
    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            rules.append({
                "type": "style",
                "selector": rule.selectorText,
                "declarations": [
                    {"property": p.name, "value": p.value, "priority": p.priority or ""}
                    for p in rule.style
                ],
            })
    return rules

def parse_with_tinycss2(css_text: str) -> List[Dict[str, Any]]:
    parsed = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    result = []
    for node in parsed:
        if node.type == "qualified-rule":
            selector = tinycss2.serialize(node.prelude).strip()
            decls = [
                {"name": d.name, "value": tinycss2.serialize(d.value).strip()}
                for d in tinycss2.parse_declaration_list(node.content)
                if d.type == "declaration"
            ]
            result.append({"selector": selector, "declarations": decls})
    return result