# interaktive Visualisierung von CSS-HTML Architekturen

- CSS files, selectors, properties, HTML nodes
- Beziehungen: selector → property, HTML element → selector, file → selector
- Graph-basierte Code-Einblicke für refactoring & audits

## Zielgruppe:
Webdesigner 

## Anwendung und Einsatzgebiete

<details>
<summary>Anwendung und Einsatzgebiete</summary>


three visualization modes: Force Graph (network view), Columns View (structured layout) and Sankey View (flow-style view) and includes:
	•	Selector clustering (file-based or semantic)
	•	Property clustering (usage buckets)
	•	Regex search + code table
	•	Legend filtering
	•	InfoPanel for rich node inspection


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


## Visualisierungtypen und Features

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


## 🧩 Clustering

Selector Clustering (clusterSelectors.js)
	•	file → Gruppierung nach Quell-CSS-Datei
	•	semantic → Gruppierung nach Namensmustern, Präfixen, Keywords

Property Clustering (clusterPropertiesByUsage.js)
	•	Gruppiert Properties dynamisch anhand der Anzahl eingehender Kanten
	•	Default: 3 Buckets (Low / Medium / High)



## Erzeugte Datasets 
	•	combined.css — alle CSS-Regeln für Regex-Analyse
	•	css_graph_with_html.json — vollständiger CSS+HTML-Graph

</details>