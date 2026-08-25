"""
Benchmark contra SOTA - Comparacion con metricas de literatura academica.
Compara metricas de red del proyecto con benchmarks publicados de futbol.
"""

import json
from pathlib import Path

try:
    import networkx as nx  # noqa: F401

    NX_AVAILABLE = True
except ImportError:
    NX_AVAILABLE = False

BENCHMARKS = {
    "density_elite": {
        "ref": "Pappalardo et al. 2019",
        "mean": 0.45,
        "range": [0.35, 0.55],
    },
    "betweenness_captain": {
        "ref": "Pedro & Coelho 2021",
        "mean": 0.38,
        "range": [0.25, 0.50],
    },
    "pagerank_top3_share": {
        "ref": "Fernandez et al. 2019",
        "mean": 0.42,
        "range": [0.35, 0.55],
    },
    "clustering_coefficient": {
        "ref": "Beal et al. 2019",
        "mean": 0.32,
        "range": [0.20, 0.45],
    },
    "n_communities": {"ref": "Gudmundsson & Horton 2017", "mean": 4, "range": [3, 6]},
}


def run_benchmark(
    data_dir: Path = Path("data/export"), output_dir: Path = Path("data/export")
) -> dict:
    if not NX_AVAILABLE:
        print("[BENCH] networkx no instalado")
        return {}

    results = {"benchmarks": BENCHMARKS, "comparisons": []}

    metrics_file = data_dir / "passing_graph_network_metrics.json"
    if metrics_file.exists():
        with open(metrics_file, encoding="utf-8") as f:
            data = json.load(f)

        density = data.get("density", 0)
        comp = {
            "metric": "density",
            "project_value": round(density, 4),
            "benchmark_mean": BENCHMARKS["density_elite"]["mean"],
        }
        in_range = (
            BENCHMARKS["density_elite"]["range"][0]
            <= density
            <= BENCHMARKS["density_elite"]["range"][1]
        )
        comp["assessment"] = "dentro_del_rango_SOTA" if in_range else "fuera_del_rango"
        results["comparisons"].append(comp)

        betweenness = data.get("top_betweenness", [])
        if betweenness:
            top_bb = betweenness[0].get("score", 0)
            comp2 = {
                "metric": "betweenness_top_player",
                "project_value": round(top_bb, 4),
                "benchmark_mean": BENCHMARKS["betweenness_captain"]["mean"],
            }
            in_range2 = (
                BENCHMARKS["betweenness_captain"]["range"][0]
                <= top_bb
                <= BENCHMARKS["betweenness_captain"]["range"][1]
            )
            comp2["assessment"] = (
                "dentro_del_rango_SOTA" if in_range2 else "fuera_del_rango"
            )
            results["comparisons"].append(comp2)

        pagerank = data.get("top_pagerank", [])
        if pagerank and len(pagerank) >= 3:
            top3_share = sum(p.get("score", 0) for p in pagerank[:3])
            comp3 = {
                "metric": "pagerank_top3_share",
                "project_value": round(top3_share, 4),
                "benchmark_mean": BENCHMARKS["pagerank_top3_share"]["mean"],
            }
            in_range3 = (
                BENCHMARKS["pagerank_top3_share"]["range"][0]
                <= top3_share
                <= BENCHMARKS["pagerank_top3_share"]["range"][1]
            )
            comp3["assessment"] = (
                "dentro_del_rango_SOTA" if in_range3 else "fuera_del_rango"
            )
            results["comparisons"].append(comp3)

        n_comm = data.get("num_communities", 0)
        if n_comm:
            comp4 = {
                "metric": "n_communities",
                "project_value": n_comm,
                "benchmark_mean": BENCHMARKS["n_communities"]["mean"],
            }
            in_range4 = (
                BENCHMARKS["n_communities"]["range"][0]
                <= n_comm
                <= BENCHMARKS["n_communities"]["range"][1]
            )
            comp4["assessment"] = (
                "dentro_del_rango_SOTA" if in_range4 else "fuera_del_rango"
            )
            results["comparisons"].append(comp4)

    in_sota = sum(
        1 for c in results["comparisons"] if c["assessment"] == "dentro_del_rango_SOTA"
    )
    total = len(results["comparisons"])
    results["summary"] = {
        "metrics_in_sota_range": in_sota,
        "total_metrics": total,
        "sota_compliance_pct": round(in_sota / total * 100, 1) if total else 0,
        "verdict": "RED COMPARABLE A EQUIPOS DE ELITE"
        if in_sota / total > 0.6
        else "RED POR DEBAJO DEL ESTANDAR SOTA"
        if total
        else "Sin datos suficientes",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "benchmark_sota.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[BENCH] {in_sota}/{total} metricas dentro del rango SOTA")
    print(f"[BENCH] Verdicto: {results['summary']['verdict']}")
    return results


if __name__ == "__main__":
    run_benchmark()
