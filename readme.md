AI-WebAnalyzer

From code cleanup to architectural insights.

<p align="center">
  <img src="./screenshot.png" alt="Graph-Screenshot" width="500">
</p>


A system for analyzing, visualizing, and optimizing CSS architectures.
Combines static code parsing, graph modeling, HTML usage mapping, and optional semantic reasoning via Ollama.

⸻

🧩 Features

<details>
<summary><strong>Click to expand</strong></summary>


🧱 CSS Structure Graph
	•	Processes CSS files in a strict, user-defined load order
	•	Extracts relationships: file → selector → property
	•	Creates enriched graph JSON: css_graph_with_html.json

🕸️ Interactive Visualization (D3.js)
	•	Force-directed graph (zoom, pan, drag)
	•	Color-coded node types (file, selector, property, HTML)
	•	Dynamic legend with toggle checkboxes
	•	Regex search for selectors or patterns
	•	Tooltips with metadata
	•	Click-to-highlight connected nodes

🌐 HTML Mapping
	•	Loads HTML from a URL
	•	Detects which selectors match real DOM elements
	•	Flags unused CSS selectors

🤖 Optional AI Analysis (Ollama)
	•	Semantic CSS refactoring
	•	Audits structure, naming, consistency
	•	Produces insights (css_graph_analysis.md)

📊 Extra Metrics
	•	Property-usage statistics
	•	Complexity & specificity scoring
	•	Live filter → shows matching CSS lines in table view

</details>



⸻

🛠️ Project Structure

<details>
<summary><strong>Folder overview</strong></summary>


AI-WebAnalyzer/
│
├── assets/
│   ├── css/style.css              # Visualization UI styles
│   └── js/                        # Modular D3 visualization logic
│       ├── main.js                # Entry point
│       ├── graph.js               # Force graph & interactions
│       ├── filter.js              # Regex-based filtering
│       ├── legend.js              # Dynamic legend component
│       ├── tooltip.js             # Hover tooltip logic
│       ├── zoom.js                # Zoom + pan
│       └── color.js               # Color mapping
│
├── ollama/
│   ├── audit.py                   # CSS audits via Ollama
│   ├── graph_analysis.py          # Semantic graph reasoning
│   ├── refactor.py                # LLM-based refactoring
│   ├── insights.py                # Metrics
│   ├── service.py                 # Handles Ollama service
│   └── utils.py                   # Helpers
│
├── output/                        # Generated analysis files
│   ├── css_graph_with_html.json   # The main graph
│   ├── css_graph_analysis.md      # AI insight report
│   └── refactored/                # Per-file refactored CSS
│
├── templates/
│   └── css_graph.html             # HTML shell for visualization
│
├── main.py                        # Orchestrates analysis workflow
├── loader.py                      # Loads & merges CSS
├── parser_css.py                  # CSS parsing
├── graph_builder.py               # Builds CSS graph
├── html_mapper.py                 # Maps selectors → HTML
├── visualizer.py                  # Writes visualization + server
├── config.py                      # Reads `.env`
├── .env                           # User configuration
├── requirements.txt               # Python deps
└── README.md                      # This document

</details>



⸻

🧠 Data Flow

<details>
<summary><strong>Processing pipeline</strong></summary>


1) Load & merge CSS

Reads configured CSS files from the folder defined in .env → produces combined.css.

2) Parse CSS

Using cssutils + tinycss2 for robustness.

3) Build Graph

Creates structured relationships:
	•	file → selector → property
	•	selector metrics (complexity, specificity)

4) HTML Mapping

Fetches HTML → identifies selector matches → marks unused selectors.

5) Graph JSON Output

Saves css_graph_with_html.json.

6) Visualization

D3.js renders interactive graph + regex search + CSS table results.

7) Optional AI Layer

Ollama performs audits, refactorings, and semantic graph reasoning.

flowchart TD
    A[Load CSS files] --> B[Combine into combined.css]
    B --> C[Parse via cssutils & tinycss2]
    C --> D[Graph Builder: file→selector→property]
    D --> E[HTML Mapper]
    E --> F[css_graph_with_html.json]
    F --> G[D3.js Visualization]
    F --> H[Ollama AI Analysis]

</details>



⸻

⚙️ Requirements & Installation

<details>
<summary><strong>Expand</strong></summary>


Requirements
	•	Python 3.9+
	•	Optional: Ollama (ollama pull codellama:7b)

Install

git clone https://github.com/your-user/AI-WebAnalyzer.git
cd AI-WebAnalyzer
pip install -r requirements.txt

Configure .env

CSS_FOLDER="/path/to/css"
CSS_ORDER=0_tokens.css,1_base.css,2_layout.css,3_components.css
OUTPUT_DIR="/path/to/output"
TARGET_URL=http://localhost:8182/public/index.php?category_id=3
OLLAMA_MODEL=codellama:7b
USE_OLLAMA=1

Run

python -m AI-WebAnalyzer.main

</details>



⸻

❤️ Credits
	•	D3.js
	•	cssutils
	•	tinycss2
	•	BeautifulSoup4
	•	Ollama

⸻

Happy analyzing & refactoring! 🎨✨