"""
Análisis de grafos de pases con NetworkX.
Calcula métricas de red: betweenness, PageRank, comunidad, diámetro.
"""

import csv
import json
from pathlib import Path

try:
    import networkx as nx

    NX_AVAILABLE = True
except ImportError:
    NX_AVAILABLE = False


def build_graph_from_csv(csv_path: Path) -> "nx.DiGraph":
    """Construye un grafo dirigido desde CSV de pases (source, target, weight)."""
    import csv

    G = nx.DiGraph()
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row.get("source", "")
            tgt = row.get("target", "")
            w = int(row.get("weight", 1))
            if src and tgt:
                G.add_edge(src, tgt, weight=w)
    return G


def run_graph_analysis(
    data_dir: Path = Path("data/export"), output_dir: Path = Path("data/export")
) -> dict:
    """
    Análisis completo de red de pases.

    Returns:
        dict con métricas de red y comunidades
    """
    if not NX_AVAILABLE:
        print("[GRAPH] NetworkX no instalado. pip install networkx")
        return {}

    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        print("[GRAPH] No CSV files found")
        return {}

    results = {}

    for csv_file in csv_files:
        G = build_graph_from_csv(csv_file)
        if len(G.nodes) < 2:
            continue

        name = csv_file.stem

        # Basic metrics
        metrics = {
            "nodes": len(G.nodes),
            "edges": len(G.edges),
            "density": nx.density(G),
            "is_connected": nx.is_weakly_connected(G)
            if nx.is_weakly_connected
            else nx.is_connected(G),
        }

        # Centrality metrics
        betweenness = nx.betweenness_centrality(G)
        pagerank = nx.pagerank(G)
        degree_cent = nx.degree_centrality(G)

        # Top 5 players by each metric
        top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
        top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:5]

        metrics["top_betweenness"] = [
            {"player": p, "score": round(s, 4)} for p, s in top_betweenness
        ]
        metrics["top_pagerank"] = [
            {"player": p, "score": round(s, 4)} for p, s in top_pagerank
        ]
        metrics["top_degree"] = [
            {"player": p, "score": round(s, 4)} for p, s in top_degree
        ]

        # Community detection (on undirected version)
        try:
            from networkx.algorithms.community import greedy_modularity_communities

            G_undir = G.to_undirected()
            communities = list(greedy_modularity_communities(G_undir))
            metrics["num_communities"] = len(communities)
            metrics["communities"] = [list(c) for c in communities[:5]]
        except Exception:  # noqa: BLE001
            metrics["num_communities"] = 0

        # PageRank as exportable data
        pagerank_data = [
            {"player": p, "pagerank": round(s, 4)}
            for p, s in sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        ]

        # Save pagerank data
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{name}_network_metrics.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

        # Save pagerank CSV
        pr_csv = output_dir / f"{name}_pagerank.csv"
        with open(pr_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["player", "pagerank"])
            writer.writeheader()
            writer.writerows(pagerank_data)

        results[name] = metrics
        print(
            f"[GRAPH] {name}: {metrics['nodes']} nodos, {metrics['edges']} aristas, {metrics.get('num_communities', '?')} comunidades"
        )
        print(
            f"  Top betweenness: {top_betweenness[0][0]} ({top_betweenness[0][1]:.3f})"
        )
        print(f"  Top pagerank: {top_pagerank[0][0]} ({top_pagerank[0][1]:.3f})")

    return results


if __name__ == "__main__":
    run_graph_analysis()
