"""Export visualization CSVs and HTML embed snippets for external tools.

Generates:
  - data/export/flourish_arc_diagram.csv
  - data/export/observable_grafo.csv
  - data/export/dw_centralidad_benchmark.csv
  - data/export/embed_snippets.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from graph_builder import build_graph, load_passing_data
from graph_analysis import run_graph_analysis

EXPORT_DIR = Path(__file__).resolve().parent.parent / "data" / "export"
SNIPPET_PATH = EXPORT_DIR / "embed_snippets.md"


def _ensure_export_dir() -> None:
    """Create the export directory if it does not exist."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def export_flourish_arc(G: nx.DiGraph) -> None:
    """Write flourish_arc_diagram.csv with edge-level centrality data."""
    betweenness = nx.betweenness_centrality(G, weight="weight")

    rows: list[dict[str, object]] = []
    for source, target, edge_data in G.edges(data=True):
        rows.append(
            {
                "source": source,
                "target": target,
                "weight": edge_data.get("weight", 1),
                "betweenness_source": round(betweenness.get(source, 0.0), 4),
                "betweenness_target": round(betweenness.get(target, 0.0), 4),
            }
        )

    df = pd.DataFrame(rows)
    out_path = EXPORT_DIR / "flourish_arc_diagram.csv"
    df.to_csv(out_path, index=False)
    print(f"[OK] flourish_arc_diagram.csv  -> {out_path}  ({len(df)} rows)")


def export_observable_grafo(G: nx.DiGraph) -> None:
    """Write observable_grafo.csv with node-level metrics."""
    betweenness = nx.betweenness_centrality(G, weight="weight")
    degree = dict(G.degree())
    in_degree = dict(G.in_degree())
    out_degree = dict(G.out_degree())

    rows: list[dict[str, object]] = []
    for node in G.nodes():
        rows.append(
            {
                "node": node,
                "betweenness": round(betweenness.get(node, 0.0), 4),
                "degree": degree.get(node, 0),
                "in_degree": in_degree.get(node, 0),
                "out_degree": out_degree.get(node, 0),
            }
        )

    df = pd.DataFrame(rows).sort_values("betweenness", ascending=False)
    out_path = EXPORT_DIR / "observable_grafo.csv"
    df.to_csv(out_path, index=False)
    print(f"[OK] observable_grafo.csv      -> {out_path}  ({len(df)} rows)")


def _assign_tactical_role(node: str, bc: float, deg: int, max_deg: int) -> str:
    """Assign a tactical role label based on centrality thresholds."""
    if bc >= 0.25:
        return "Playmaker Critico"
    if deg >= max_deg * 0.75:
        return "Distribuidor Volumen"
    if bc >= 0.10:
        return "Enlace Transicional"
    return "Jugador de Apoyo"


def export_dw_centralidad(G: nx.DiGraph) -> None:
    """Write dw_centralidad_benchmark.csv with per-player centrality + role."""
    betweenness = nx.betweenness_centrality(G, weight="weight")
    degree_cent = nx.degree_centrality(G)
    degree = dict(G.degree())
    max_deg = max(degree.values()) if degree else 1

    rows: list[dict[str, object]] = []
    for node in G.nodes():
        bc = betweenness.get(node, 0.0)
        dc = degree_cent.get(node, 0.0)
        deg = degree.get(node, 0)
        rows.append(
            {
                "player": node,
                "betweenness": round(bc, 4),
                "degree_centrality": round(dc, 4),
                "tactical_role": _assign_tactical_role(node, bc, deg, max_deg),
            }
        )

    df = pd.DataFrame(rows).sort_values("betweenness", ascending=False)
    out_path = EXPORT_DIR / "dw_centralidad_benchmark.csv"
    df.to_csv(out_path, index=False)
    print(f"[OK] dw_centralidad_benchmark.csv -> {out_path}  ({len(df)} rows)")


def generate_embed_snippets() -> None:
    """Write embed_snippets.md with responsive HTML iframes."""
    snippet = """# Embed Snippets - Tactical Network Visualizations

Copy the HTML snippets below into your portfolio or report.
Each snippet is responsive and mobile-friendly.

---

## 1. Flourish Arc / Chord Diagram

```html
<div style="width:100%;max-width:960px;margin:0 auto;">
  <iframe
    src="https://public.flourish.studio/visualisation/YOUR_VISUALISATION_ID/embed"
    title="Flourish Arc Diagram - Passing Network"
    style="width:100%;height:600px;border:none;"
    loading="lazy"
    allowfullscreen
  ></iframe>
</div>
```

---

## 2. Observable Force-Directed Graph

```html
<div style="width:100%;max-width:960px;margin:0 auto;">
  <iframe
    src="https://observablehq.com/embed/@YOUR_USERNAME/tactical-force-graph?cell=valueof"
    title="Observable Force Graph - Tactical Network"
    style="width:100%;height:650px;border:1px solid #e0e0e0;border-radius:4px;"
    loading="lazy"
    allowfullscreen
  ></iframe>
</div>
```

---

## 3. Datawrapper Bar Chart (Centrality Benchmark)

```html
<div style="width:100%;max-width:800px;margin:0 auto;">
  <iframe
    src="https://datawrapper.de/YOUR_CHART_ID/"
    title="Datawrapper - Betweenness Centrality Benchmark"
    style="width:100%;height:480px;border:none;"
    loading="lazy"
    allowfullscreen
    scrolling="no"
  ></iframe>
</div>
```
"""
    SNIPPET_PATH.write_text(snippet, encoding="utf-8")
    print(f"[OK] embed_snippets.md          -> {SNIPPET_PATH}")


def main() -> None:
    """Orchestrate graph build, analysis, CSV export and snippet generation."""
    try:
        _ensure_export_dir()

        df = load_passing_data()
        G = build_graph(df)

        print(
            f"\nGraph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n"
        )

        export_flourish_arc(G)
        export_observable_grafo(G)
        export_dw_centralidad(G)
        generate_embed_snippets()

        run_graph_analysis()

        from benchmark_sota import run_benchmark
        run_benchmark()

        from statistical_tests import run_statistical_tests
        run_statistical_tests()

        from generate_tables import generate as generate_exec_tables
        generate_exec_tables()

        print("\nAll exports completed successfully.")
    except (OSError, ValueError, KeyError) as exc:
        print(f"[ERROR] Export failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
