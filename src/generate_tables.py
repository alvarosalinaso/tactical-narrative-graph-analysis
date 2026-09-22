"""Genera tabla ejecutiva de métricas de red con fallback a pandas styling"""

import json
from pathlib import Path

import pandas as pd


def generate():
    metrics_file = Path("data/export/passing_graph_network_metrics.json")
    if not metrics_file.exists():
        print(
            "[TABLE] network_metrics.json no encontrado — ejecutar graph_analysis.py primero"
        )
        return

    with open(metrics_file, encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for player_data in data.get("top_betweenness", []):
        rows.append(
            {
                "Métrica": "Betweenness",
                "Jugador": player_data["player"],
                "Valor": player_data["score"],
            }
        )
    for player_data in data.get("top_pagerank", []):
        rows.append(
            {
                "Métrica": "PageRank",
                "Jugador": player_data["player"],
                "Valor": player_data["score"],
            }
        )

    df = pd.DataFrame(rows)

    # Try great_tables first, fallback to pandas styling
    try:
        from great_tables import GT

        tbl = (
            GT(df)
            .tab_header(title="Métricas de Red — Grafo de Pases Tácticos")
            .tab_source_note("Fuente: NetworkX | Análisis: Álvaro Salinas")
        )
        Path("assets").mkdir(exist_ok=True)
        tbl.save("assets/executive_table.html")
        print("[TABLE] assets/executive_table.html generado (great_tables)")
    except ImportError:
        # Fallback: pandas styling
        styled = (
            df.style.set_caption("Métricas de Red — Grafo de Pases Tácticos")
            .set_table_styles(
                [
                    {
                        "selector": "caption",
                        "props": [("font-size", "16px"), ("font-weight", "bold")],
                    },
                    {
                        "selector": "th",
                        "props": [
                            ("background-color", "#533483"),
                            ("color", "white"),
                            ("font-weight", "bold"),
                        ],
                    },
                    {"selector": "td", "props": [("border", "1px solid #ddd")]},
                ]
            )
            .format(precision=4)
            .hide(axis="index")
        )
        Path("assets").mkdir(exist_ok=True)
        styled.to_html("assets/executive_table.html")
        print("[TABLE] assets/executive_table.html generado (pandas styling fallback)")


if __name__ == "__main__":
    generate()
