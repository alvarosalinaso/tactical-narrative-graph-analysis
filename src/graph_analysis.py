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

# Semilla fija para que la deteccion de comunidades sea reproducible
COMMUNITY_SEED = 42


def build_graph_from_csv(csv_path: Path) -> "nx.DiGraph":
    """Construye un grafo dirigido desde CSV de pases (source, target, weight)."""

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


def betweenness_weighted(G: "nx.DiGraph") -> dict:
    """Betweenness ponderado con distancia = 1/weight (frecuencia de pases).

    NetworkX interpreta ``weight`` como distancia, así que la frecuencia se
    invierte: cuanto más pases entre dos jugadores, más corta la arista y más
    preferido es ese carril por los caminos más cortos.
    """
    H = nx.DiGraph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from(
        (u, v, {"distance": 1.0 / d["weight"]})
        for u, v, d in G.edges(data=True)
        if d.get("weight")
    )
    return nx.betweenness_centrality(H, weight="distance")


def compute_metrics(G: "nx.DiGraph") -> dict:
    """Calcula métricas completas de una red de pases (un solo equipo).

    Betweenness se calcula en dos versiones (sin pesos y con distancia
    1/weight); degree sin pesos y PageRank con el peso de frecuencia de
    pases. Las comunidades se detectan sobre la versión no dirigida.
    """
    betweenness = nx.betweenness_centrality(G)
    pagerank = nx.pagerank(G, weight="weight")
    degree_cent = nx.degree_centrality(G)

    try:
        from networkx.algorithms.community import louvain_communities

        # louvain_communities acepta seed (greedy_modularity_communities, no).
        communities = [
            sorted(c)
            for c in louvain_communities(
                G.to_undirected(), weight="weight", seed=COMMUNITY_SEED
            )
        ]
    except Exception:  # noqa: BLE001
        communities = []

    return {
        "nodes": len(G.nodes),
        "edges": len(G.edges),
        "density": nx.density(G),
        "is_connected": nx.is_weakly_connected(G),
        "betweenness": betweenness,
        "betweenness_weighted": betweenness_weighted(G),
        "pagerank": pagerank,
        "degree_centrality": degree_cent,
        "in_degree": dict(G.in_degree(weight="weight")),
        "out_degree": dict(G.out_degree(weight="weight")),
        "communities": communities,
    }


def summarize_metrics(metrics: dict, top_n: int = 5) -> dict:
    """Resumen serializable de ``compute_metrics`` (top-N por métrica)."""

    def top_n_list(scores: dict) -> list[dict]:
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [{"player": p, "score": round(s, 4)} for p, s in ranked]

    communities = metrics.get("communities", [])
    return {
        "nodes": metrics["nodes"],
        "edges": metrics["edges"],
        "density": metrics["density"],
        "is_connected": metrics["is_connected"],
        "top_betweenness": top_n_list(metrics["betweenness"]),
        "top_betweenness_weighted": top_n_list(metrics["betweenness_weighted"]),
        "top_pagerank": top_n_list(metrics["pagerank"]),
        "top_degree": top_n_list(metrics["degree_centrality"]),
        "num_communities": len(communities),
        "communities": [list(c) for c in communities[:5]],
    }


def run_graph_analysis(
    data_dir: Path = Path("data/export"), output_dir: Path = Path("data/export")
) -> dict:
    """
    Análisis completo de red de pases (un grafo por CSV, es decir, por equipo).

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
        full_metrics = compute_metrics(G)
        metrics = summarize_metrics(full_metrics)
        pagerank = full_metrics["pagerank"]

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
        top_betweenness = metrics["top_betweenness"]
        top_pagerank = metrics["top_pagerank"]
        print(
            f"[GRAPH] {name}: {metrics['nodes']} nodos, {metrics['edges']} aristas, {metrics.get('num_communities', '?')} comunidades"
        )
        if top_betweenness:
            print(
                f"  Top betweenness: {top_betweenness[0]['player']} ({top_betweenness[0]['score']:.3f})"
            )
        if top_pagerank:
            print(
                f"  Top pagerank: {top_pagerank[0]['player']} ({top_pagerank[0]['score']:.3f})"
            )

    return results


if __name__ == "__main__":
    run_graph_analysis()
