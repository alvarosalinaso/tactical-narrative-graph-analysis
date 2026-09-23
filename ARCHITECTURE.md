# Arquitectura — tactical-narrative-graph-analysis

## Visión general
Análisis de redes de pases (StatsBomb Open Data). Grafo dirigido de pases entre jugadores, métricas de centralidad (betweenness, PageRank), detección de comunidades, visualización interactiva (pyvis).

## Componentes principales

### Datos
- `data/raw/statsbomb_passes.csv` — Event-level passes (passer, receiver, pass_length, pass_outcome, minute, team, opponent)
- `data/raw/match_info.json` — Metadatos del partido
- `data/raw/passing.csv` — Fallback: aggregate passing stats (Player, Pos, Cmp, PrgP)
- `data/export/*_network_metrics.json` — Métricas por red
- `data/export/*_pagerank.csv` — PageRank por jugador
- `output/grafo_tactico.html` — Visualización pyvis

### Procesamiento (src/)
- `graph_builder.py`:
  - `load_passing_data()`: StatsBomb → edges agregados (weight, avg_length, completion_rate, type)
  - `_load_aggregate_stats()`: Fallback passing.csv → edges sintéticos por posición (ILUSTRATIVO, no comparable con eventos StatsBomb)
  - `build_graph()`: DataFrame → nx.DiGraph
  - `analyze_and_visualize()`: centrality + pyvis → HTML interactivo (betweenness sin peso; PageRank/degree con peso de frecuencia)
- `graph_analysis.py`:
  - `build_graph_from_csv()`: CSV (source, target, weight) → nx.DiGraph
  - `run_graph_analysis()`: density, centrality (betweenness sin peso; PageRank/degree con peso), comunidades (greedy_modularity), exporta JSON + CSV
- `benchmark_sota.py` — run_benchmark: comparación con literatura
- `statistical_tests.py` — run_statistical_tests
- `generate_tables.py` — generate
- `export_visualizations.py` — export_visualizations
- `analyze_all.py` — Orquestador

## Flujo de datos
```
statsbomb_passes.csv → load_passing_data → edges DataFrame
edges → build_graph → nx.DiGraph
nx.DiGraph → analyze_and_visualize → output/grafo_tactico.html
CSV exports → run_graph_analysis → *_network_metrics.json + *_pagerank.csv
```

## Despliegue
- No tiene render.yaml (proyecto de análisis, no dashboard web)
- Outputs: HTML estático + JSON/CSV

## Tests
- `tests/test_analysis.py` — Smoke tests + load_passing_data, build_graph, graph_analysis, statistical_tests
- `tests/test_graph_builder.py` — build_graph, load_passing_data (con mocks)
- `tests/test_graph_analysis.py` — build_graph_from_csv, run_graph_analysis (con mocks)
- CI: pytest + coverage + ruff (Python 3.10, 3.11, 3.12)

## Dependencias clave
- networkx, pyvis, pandas
- StatsBomb Open Data (requiere descarga manual o script download_real_data.py)