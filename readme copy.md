## CSS Analyse mit Ollama

from “code cleanup” to architectural insight.

multi-phase Ollama analysis layer that eats CSS and graph data from it. It combines structured data (the css_graph.json) and semantic reasoning from Ollama.

### css-analyzer-ollama
```txt
📁 css-analyzer-ollama/
│
├── __init__.py
├── config.py
├── main.py
│
├── ollama/
│   ├── __init__.py
│   ├── service.py          ← start/stop/status
│   ├── refactor.py         ← refactor CSS only
│   ├── audit.py            ← structural audit of CSS
│   ├── graph_analysis.py   ← graph-based reasoning
│   └── utils.py            ← shared sanitization / helpers
│
└── visualizer.py


output/
 ├── css_graph.html         ← lightweight HTML shell
 ├── js/
 │   ├── main.js            ← entry point
 │   ├── graph.js           ← handles rendering & simulation
 │   ├── tooltip.js         ← manages tooltip logic
 │   ├── zoom.js            ← zoom/pan + shortcuts
 │   └── colors.js          ← color + style definitions
 └── css/
     └── style.css
```

python3 -m css-analyzer-ollama.main

stop the server

Press Ctrl+C.
This sends SIGINT to the Python process and the server should shut down cleanly.
### AI-WebAnalyzer

Summary
	•	main.py = Orchestrates everything
	•	ollama/ = AI logic (refactor, audit, graph insights)
	•	templates/js/ = Modular D3 visualization
	•	output/ = Generated reports + visual graph
	•	html_mapper.py = HTML-to-CSS graph linking
	•	config.py + .env = All settings centralized

```txt
AI-WebAnalyzer/
│
├── css/
│   └── style.css
│       → Global stylesheet for the visualization UI (used by D3 graph pages).
│         Defines the dark background, font, tooltip look, etc.
│
├── templates/
│   ├── css_graph.html
│   │   → Minimal HTML shell for the D3 visualization.
│   │     Loads `d3.v7`, your modular JS files, and references `../css/style.css`.
│   │     Copied automatically into `/output/` when you run the analyzer.
│   │
│   └── js/
│       ├── main.js
│       │   → Entry point for the visualization.
│       │     Loads `css_graph.json`, sets up the SVG canvas,
│       │     and initializes zoom + rendering logic.
│       │
│       ├── graph.js
│       │   → Core D3 logic: creates force simulation,
│       │     draws nodes, links, handles drag, and updates positions on tick.
│       │
│       ├── tooltip.js
│       │   → Tooltip behavior (mouseover, move, mouseout).
│       │     Handles node highlighting and link emphasis.
│       │
│       ├── zoom.js
│       │   → Configures D3 zooming and panning behavior.
│       │     Also supports keyboard shortcuts (e.g. "0" to reset zoom).
│       │
│       └── color.js
│           → Central color map for node and link types (file, selector, property, html).
│
├── output/
│   ├── css_graph.json           → Generated visualization data (nodes + links).
│   ├── css_graph.html           → Final HTML visualization (copied from template).
│   ├── css_graph_analysis.md    → Ollama-generated CSS graph intelligence insights.
│   ├── css_audit.md             → Ollama audit report about CSS structure and redundancy.
│   ├── combined.css             → Merged raw CSS from all input files.
│   ├── combined.refactored.css  → Refactored CSS after Ollama optimization.
│   ├── css_graph_with_html.json → Extended graph linking HTML DOM nodes to CSS selectors.
│   └── refactored/              → Per-file refactored CSS outputs.
│
├── ollama/
│   ├── audit.py
│   │   → Sends project CSS to Ollama for a structural audit.
│   │     Detects redundancy, complexity, or unused parts.
│   │
│   ├── graph_analysis.py
│   │   → Uses Ollama to analyze your D3 graph JSON.
│   │     Describes selector relationships, overconnections, and modular suggestions.
│   │
│   ├── refactor.py
│   │   → Sends each CSS file (and combined.css) to Ollama for semantic cleanup
│   │     — merges duplicates, simplifies variables, standardizes formatting.
│   │
│   ├── service.py
│   │   → Handles starting, checking, and stopping the Ollama service
│   │     (via Homebrew on macOS or manual startup).
│   │
│   ├── utils.py
│   │   → Utility helpers for Ollama modules (CSS validation, safe JSON parsing, etc.).
│   │
│   └── __init__.py
│       → Makes the `ollama` directory a proper Python package.
│
├── main.py
│   → Central orchestrator.
│     - Loads and combines CSS files
│     - Parses CSS via `cssutils` + `tinycss2`
│     - Builds and saves D3 graph JSON
│     - Optionally runs Ollama-based refactor, audit, and graph analysis
│     - Launches local webserver for visualization
│
├── visualizer.py
│   → Responsible for:
│     - Writing the D3 HTML template + assets to `/output/`
│     - Serving the visualization on a local webserver (http://localhost:8080)
│
├── html_mapper.py
│   → Fetches an HTML page from the configured `TARGET_URL`
│     and extends the CSS graph with HTML element nodes that match CSS selectors.
│
├── loader.py
│   → Loads and merges CSS files based on `.env` settings.
│     Maintains the correct load order defined in `CSS_ORDER`.
│
├── graph_builder.py
│   → Parses all CSS rules and builds a dependency graph (files → selectors → properties).
│     Adds metrics like declaration/usage counts for visualization.
│
├── parser_css.py
│   → CSS parsing interface combining `cssutils` and `tinycss2` results
│     for redundancy and cross-validation of rules.
│
├── config.py
│   → Loads environment variables from `.env` (via `python-dotenv`).
│     Provides easy access to settings like model, folders, URL, etc.
│
├── .env
│   → Environment configuration file.
│     Contains paths, Ollama model setup, and feature toggles.
│     Example:
│     ```
│     CSS_FOLDER="/path/to/css"
│     CSS_ORDER=base.css,layout.css,theme.css
│     OLLAMA_MODEL=codellama:7b
│     OLLAMA_URL=http://localhost:11434
│     USE_OLLAMA=1
│     OUTPUT_DIR="./output"
│     TARGET_URL=http://localhost:8182/public/index.php?category_id=3
│     ```
│
└── readme.md
    → Project documentation, setup guide, and usage instructions.
```
### .env configuration

```dotenv
CSS_FOLDER="/somewhere/css"
CSS_ORDER=0_tokens.css,1_base.css,2_layout.css,3_components.css,3_motion.css
OLLAMA_MODEL=codellama:7b
OLLAMA_URL=http://localhost:11434
USE_OLLAMA=1
CHAR_LIMIT=100000
OUTPUT_DIR="/Users/thomassalomon/Library/Mobile Documents/com~apple~CloudDocs/Documents/_OFFICE/Projects-Web/DESIGN_XVIZ/css-analyzer-ollama/output"
TARGET_URL=http://localhost:8182/public/index.php?category_id=3


