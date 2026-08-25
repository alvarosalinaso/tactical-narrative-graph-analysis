# Tactical Passing Network Analysis

[![CI](https://github.com/alvarosalinaso/tactical-narrative-graph-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/tactical-narrative-graph-analysis/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)

---

## What is this?

EN: I wanted to see if network graph analysis could reveal tactical patterns in football passing data that traditional stats miss. So I built a pipeline that takes FBref passing data, constructs a directed graph with NetworkX, and calculates centrality metrics to identify key players and structural weaknesses.

ES: Quería ver si el análisis de grafos de red podía revelar patrones tácticos en datos de pases de fútbol que las estadísticas tradicionales pasan por alto. Construí un pipeline que toma datos de FBref, construye un grafo dirigido con NetworkX y calcula métricas de centralidad para identificar jugadores clave y debilidades estructurales.

---

## Questions I asked

**P1 - Single Point of Failure:** Is there a player whose removal would collapse the team's possession network? Betweenness centrality should identify these structural vulnerabilities.

**P2 - Traffic monopolies:** Does one midfielder concentrate a disproportionate share of transitional traffic? If so, opponents can target this player to disrupt buildup.

**P3 - Failed connections:** Are there missing links between midfielders and forwards that traditional stats don't show? The graph can reveal where tactical communication breaks down.

---

## How it works

### 1. Graph construction

`src/graph_builder.py` builds a `nx.DiGraph` from passing events:
- **Nodes** = players
- **Directed edges** = passing direction
- **Edge weight** = accumulated pass frequency

### 2. Centrality metrics

| Metric | What it measures |
|--------|-----------------|
| **Degree Centrality** | Who receives and distributes the most ball volume |
| **Betweenness Centrality** | Who acts as indispensable bridge between defense and attack (the SPOF) |
| **Closeness Centrality** | Who is closest to all other players by average pass distance |

### 3. Interactive visualization

PyVis renders the graph as an interactive HTML file (`output/grafo_tactico.html`) with force-directed layout. Node size reflects betweenness centrality.

---

## Key findings

- Bruno Fernandes monopolizes ~45% of transitional traffic — a clear single point of failure
- 3 communities detected, matching expected tactical blocks (defense, midfield, attack)
- Missing edges between midfielders and forwards reveal communication breakdowns in interior channels

---

## Visualizations

<details>
<summary><strong>Datawrapper — Centrality benchmark</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://datawrapper.dwcdn.net/ahvhZ/" title="Centrality Benchmark" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Observable — Interactive graph</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://observablehq.com/@alvarosalinaso/tactical-nodes" title="Tactical Passing Graph" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

---

## How to run

```bash
git clone https://github.com/alvarosalinaso/tactical-narrative-graph-analysis
cd tactical-narrative-graph-analysis
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python src/graph_builder.py
```

Open `output/grafo_tactico.html` in your browser.

---

## Dependencies

```
networkx==3.2.1
pyvis==0.3.2
pandas==2.2.1
```

---

> **Álvaro Salinas Ortiz**
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portfolio](https://alvarosalinaso.github.io/portfolio-web/)
