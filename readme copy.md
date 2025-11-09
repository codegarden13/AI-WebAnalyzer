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


