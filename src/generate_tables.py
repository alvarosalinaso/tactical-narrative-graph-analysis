"""Genera tabla ejecutiva de métricas de red con great_tables"""
import json
from pathlib import Path
from great_tables import GT
import pandas as pd

def generate():
    metrics_file = Path("data/export/passing_graph_network_metrics.json")
    if not metrics_file.exists():
        print("[TABLE] network_metrics.json no encontrado — ejecutar graph_analysis.py primero")
        return
    
    with open(metrics_file, encoding="utf-8") as f:
        data = json.load(f)
    
    rows = []
    for player_data in data.get("top_betweenness", []):
        rows.append({"Métrica": "Betweenness", "Jugador": player_data["player"], "Valor": player_data["score"]})
    for player_data in data.get("top_pagerank", []):
        rows.append({"Métrica": "PageRank", "Jugador": player_data["player"], "Valor": player_data["score"]})
    
    df = pd.DataFrame(rows)
    
    tbl = (
        GT(df)
        .tab_header(title="Métricas de Red — Grafo de Pases Tácticos")
        .tab_source_note("Fuente: NetworkX | Análisis: Álvaro Salinas")
    )
    Path("assets").mkdir(exist_ok=True)
    tbl.save("assets/executive_table.html")
    print("[TABLE] assets/executive_table.html generado")

if __name__ == "__main__":
    generate()
