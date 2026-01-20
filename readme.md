## Purpose

CSS Graph Visualizer analyzes and visualizes the architecture of CSS + HTML for a website:
- CSS files, selectors, properties, HTML nodes
	•	Relationships: selector → property, HTML element → selector, file → selector
	•	Graph-based insights for refactoring & audits

It provides three visualization modes: Force Graph (network view), Columns View (structured layout) and Sankey View (flow-style view) and includes:
	•	Selector clustering (file-based or semantic)
	•	Property clustering (usage buckets)
	•	Regex search + code table
	•	Legend filtering
	•	InfoPanel for rich node inspection

⸻

🧱 Project Structure

```text
assets/
  css/
    style.css

  js/
    main.js
    forceGraph.js
    columnsView.js
    sankeyGraph.js

    clusterSelectors.js
    clusterPropertiesByUsage.js

    legend.js
    filter.js
    table.js
    color.js

    infoPanel.js
    tooltip.js
    zoom.js

combined.css
css_graph_with_html.json
```


⸻

## Workflow

1) Build CSS Graph (graph_builder.py)
	•	Extrahiert Selektoren & Properties
	•	Erzeugt uses-Beziehungen
	•	Bewertet Komplexität, Spezifität, Nutzung
	•	Gibt css_graph.json aus

2) HTML Mapping (html_mapper.py)
	•	Verknüpft DOM-Elemente mit CSS-Selektoren
	•	Markiert ungenutzte Selektoren
	•	Fügt HTML-Knoten + matches-Kanten hinzu
	•	Gibt css_graph_with_html.json aus

3) Frontend Visualisierung (main.js)
	•	Lädt Graph-JSON
	•	Rendert Force / Columns / Sankey
	•	Aktiviert Zoom, Legend-Toggle, InfoPanel, Filter, Clustering
	•	Nutzt combined.css für Regex-Suche

⸻

📊 Visualization Modes

1. Force Graph
	•	Physikbasierte Netzvisualisierung
	•	Zeigt Gesamtzusammenhänge
	•	Drag, Zoom, Highlighting

2. Columns View
	•	Klare Spalten: Files → Selector-Cluster → Properties
	•	Ideal für Debugging & Architektur-Übersicht
	•	InfoPanel rechts
	•	Unterstützt Selector-Clustering

3. Sankey View
	•	Flussorientiert: Files → Selectors → Property-Cluster
	•	Linkdicke = Nutzungshäufigkeit
	•	Properties gruppiert in Usage-Buckets

⸻

🔍 Interaction Features
	•	Legend Filtering – Typen ein/ausblenden
	•	Regex Filter – beeinflusst Graph + Code-Tabelle
	•	Hover – Preview im InfoPanel
	•	Click – InfoPanel pinnen
	•	Zoom / Pan – Maus + Drag
	•	0 – Zoom Reset

⸻

🧩 Clustering

Selector Clustering (clusterSelectors.js)
	•	file → Gruppierung nach Quell-CSS-Datei
	•	semantic → Gruppierung nach Namensmustern, Präfixen, Keywords

Property Clustering (clusterPropertiesByUsage.js)
	•	Gruppiert Properties dynamisch anhand der Anzahl eingehender Kanten
	•	Default: 3 Buckets (Low / Medium / High)

⸻

🖥️ HTML Layout

<div id="layout">
  <div id="topRow">
    <div id="controls"></div>
    <div id="graph"></div>
    <div id="infoPanel"></div>
  </div>
  <div id="codeView"></div>
</div>


⸻

📦 Data Sources
	•	combined.css — alle CSS-Regeln für Regex-Analyse
	•	css_graph_with_html.json — vollständiger CSS+HTML-Graph

⸻

🧪 Ideas for Future Enhancements
	•	Dynamische Clusteranzahl
	•	Property-Kategorien (typography / layout / animation / misc)
	•	HTML-Knoten optional sichtbar machen
	•	Minimap für ForceGraph
	•	Caching und History-Vergleich zwischen Versionen

⸻

✔️ TL;DR
	•	Backend erzeugt Graph-JSON (CSS + HTML)
	•	Frontend bietet 3 interaktive Visualisierungen
	•	Clusterung, Filtering, InfoPanel = tiefe Einsichten
	•	Perfekt für CSS-Audits, Refactoring, Style-System-Analyse

