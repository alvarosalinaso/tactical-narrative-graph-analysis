# Tactical Passing Network Analysis

[![CI](https://github.com/alvarosalinaso/tactical-narrative-graph-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/tactical-narrative-graph-analysis/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)

---

## What is this?

EN: Network graph analysis on real football passing data to reveal tactical patterns that traditional stats miss. Uses StatsBomb Open Data (event-level passes with actual player names and locations) to construct directed graphs and calculate centrality metrics.

ES: Análisis de grafos de red sobre datos reales de pases de fútbol para revelar patrones tácticos que las estadísticas tradicionales no muestran. Usa datos abiertos de StatsBomb (pases a nivel de evento con nombres reales de jugadores y ubicaciones) para construir grafos dirigidos y calcular métricas de centralidad.

---

## Data Source

**StatsBomb Open Data** — Free, event-level football data:
- Real pass events with player names, locations, and outcomes
- World Cup 2022 matches (Morocco vs Canada as demo)
- 869 total passes → 252 unique passing edges

---

## Questions I asked

**P1 - Single Point of Failure:** Is there a player whose removal would collapse the team's possession network? Betweenness centrality identifies these structural vulnerabilities.

**P2 - Traffic monopolies:** Does one player concentrate a disproportionate share of transitional traffic? Opponents can target this player to disrupt buildup.

**P3 - Failed connections:** Are there missing links between midfielders and forwards that traditional stats don't show? The graph reveals where tactical communication breaks down.

---

## How it works

### 1. Graph construction

`src/graph_builder.py` builds a `nx.DiGraph` from StatsBomb passing events:
- **Nodes** = players (real names from match data)
- **Directed edges** = actual pass direction between players
- **Edge weight** = accumulated pass frequency

### 2. Centrality metrics

| Metric | What it measures |
|--------|-----------------|
| **Betweenness Centrality** | Who acts as indispensable bridge (the SPOF) |
| **PageRank** | Who is most connected in the passing network |
| **In/Out Degree** | Ball reception vs distribution volume |

**Centrality variants — which is which:**

- **Betweenness unweighted** (`top_betweenness`): every pass hop counts as 1. Answers "who sits on the most minimum-hop paths" — this is the one used for node size in the interactive graph and for the headline rankings.
- **Betweenness weighted** (`top_betweenness_weighted`, distance = 1/weight): frequent pass lanes become *short* edges, so shortest paths prefer high-frequency connections. Answers "who bridges the frequent-pass cores". NetworkX treats `weight` as distance, hence the inversion.
- **PageRank / degree**: use pass frequency as weight (frequency = importance).

The pipeline has no synthetic fallback: without `data/raw/statsbomb_passes.csv` it stops with a warning and builds nothing, so no centrality can come from fabricated edges. The old `passing.csv` FBref/United fallback was removed.

### 3. Interactive visualization

PyVis renders the graph as an interactive HTML file (`output/grafo_tactico.html`) with force-directed layout. Node size reflects betweenness centrality.

---

## Key findings (Morocco vs Canada)

- Sofyan Amrabat has highest betweenness (0.0245, unweighted, StatsBomb event graph) — key connector in Morocco's buildup (Azzedine Ounahi 0.0158, 4th)
- 252 unique passing edges from 869 total passes
- Short passes (<10m) dominate possession phases
- Long balls (>25m) used primarily in transitions

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
networkx>=3.0
pyvis>=0.3
pandas>=2.0
statsbombpy>=1.0
```

---

## Related projects

- [Manchester United Analysis](https://github.com/alvarosalinaso/manchester-united-analisis) — Causal analysis of managerial changes
- [Chilean Video Games](https://github.com/alvarosalinaso/chilean-videogames-analysis) — Market analysis with scraping
- [World Cup 2026](https://github.com/alvarosalinaso/worldcup-2026) — Interactive dashboard

---

> **Álvaro Salinas Ortiz**
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portfolio](https://alvarosalinaso.github.io/portfolio-web/)
