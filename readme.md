# AI-WebAnalyzer

*First KI tool, started oct-2025.* 😎

Dev tool for analyzing, visualizing, and optimizing CSS architectures.

Combines static analysis (parsing, graph modeling, metrics) with an interactive D3.js visualization (and optional AI-powered insights via Ollama).

<p align="center">
  <img src="./screenshot.png" alt="Graph-Screenshot" width="500">
</p>

- loads your CSS files in a defined order, extracts all dependencies (file → selector → property), and builds a structural graph. Optionally, it fetches an HTML reference page to detect which selectors are actually used and to highlight unused or redundant parts of your styles.

- web interface renders the full relationship graph with zooming, tooltips, filtering, a dynamic legend, and a live table showing all matching CSS lines via regex.
With Ollama enabled, the system can also produce refactoring suggestions, audits, and semantic insights.

In short:
👉 A practical tool that makes large or legacy CSS codebases more understandable, analyzable, and refactor-friendly.

## Features

<details>
<summary>Features</summary>



### 🧩 CSS Structure Graph
- Processes CSS files in strict order
- Creates a logical model of file → selector → property
- Outputs not only css_graph_with_html.json for visualization

🕸️ Interactive D3.js Visualization
- Force-directed graph with zoom & pan
- Color-coded node types (file, selector, property, HTML)
- Dynamic legend with checkboxes to toggle types
- Regex-based search that filters both graph nodes and CSS lines
- Hover tooltips with detailed metadata

### 🌐 HTML Mapping
- Loads a reference HTML page (URL or file)
- Detects which selectors actually match real DOM elements
- Highlights unused CSS selectors

### 🤖 Optional AI Support (Ollama)
- Semantic CSS refactoring
- Structural audits and naming consistency checks
- Graph-based insights using large language models

### 📊 Extra Metrics
- CSS summaries with property frequencies
- Complexity and specificity scoring for selectors
- css_graph_analysis.md with semantic graph insights
</details>

## Project Structure
<details>
<summary>Project Structure</summary>


```text
AI-WebAnalyzer/
│
├── assets/
│   ├── css/style.css              # Global stylesheet for the D3 UI
│   └── js/                        # Modular D3 visualization scripts
│       ├── main.js                # Entry point
│       ├── graph.js               # Force graph logic
│       ├── filter.js              # Regex filtering
│       ├── legend.js              # Dynamic legend
│       ├── tooltip.js             # Hover tooltip behavior
│       ├── zoom.js                # Zoom & pan
│       └── color.js               # Color definitions
│
├── ollama/
│   ├── audit.py                   # Runs CSS audits using Ollama
│   ├── graph_analysis.py          # Semantic graph analysis
│   ├── refactor.py                # Refactors CSS via LLM
│   ├── insights.py                # Generates metrics
│   ├── service.py                 # Manages Ollama service
│   └── utils.py                   # Utility functions
│
├── output/                        # Generated artifacts
│   ├── css_graph_with_html.json   # Main graph
│   ├── css_graph_analysis.md      # AI-generated insights
│   └── refactored/                # Per-file refactored CSS
│
├── templates/
│   └── css_graph.html             # HTML shell for visualization
│
├── main.py                        # Orchestrator: CSS → Graph → Server
├── loader.py                      # CSS loading & merging
├── parser_css.py                  # CSS parsing (cssutils + tinycss2)
├── graph_builder.py               # Builds node/link relationships
├── html_mapper.py                 # HTML → CSS matching
├── visualizer.py                  # Copies template & starts web server
├── config.py                      # Reads settings from `.env`
├── .env                           # User configuration
├── requirements.txt               # Python dependencies
└── README.md                      # Documentation

```

</details>

## Requirements
- Python 3.9+
- Optional: Ollama for AI analysis (ollama pull codellama:7b)

## Clone Repository

```sh
git clone https://github.com/your-user/AI-WebAnalyzer.git
cd AI-WebAnalyzer

Install Dependencies

pip install -r requirements.txt
```




## 🛠️ Usage

Step 1 — Configure .env, example:

CSS_FOLDER="/path/to/css/files"
CSS_ORDER=0_tokens.css,1_base.css,2_layout.css,3_components