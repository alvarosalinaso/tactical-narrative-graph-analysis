"""Tests estadisticos para analisis de grafos tacticos."""
import json
from pathlib import Path

try:
    import numpy as np
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def run_statistical_tests(data_dir: Path = Path("data/export"), output_dir: Path = Path("data/export")) -> dict:
    if not SCIPY_AVAILABLE:
        return {}

    results = {}

    metrics_file = data_dir / "passing_graph_network_metrics.json"
    if metrics_file.exists():
        with open(metrics_file, encoding="utf-8") as f:
            data = json.load(f)

        betweenness = [e["score"] for e in data.get("top_betweenness", [])]
        pagerank = [e["score"] for e in data.get("top_pagerank", [])]

        if len(betweenness) == len(pagerank) and len(betweenness) > 2:
            r, p = stats.spearmanr(betweenness, pagerank)
            results["spearman_betweenness_pagerank"] = {
                "test": "Spearman rank correlation",
                "h0": "No hay asociacion entre betweenness y PageRank",
                "rho": round(r, 4),
                "p_value": round(p, 6),
                "significant": p < 0.05,
                "interpretation": "Los jugadores con alta betweenness tambien tienen alto PageRank" if r > 0.5 else "Metricas independientes",
            }
            print(f"[STATS] Spearman: rho={r:.3f}, p={p:.4f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results
