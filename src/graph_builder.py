from __future__ import annotations

import os
from pathlib import Path

import networkx as nx
import pandas as pd
from pyvis.network import Network

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PASSING_CSV = DATA_DIR / "passing.csv"


def load_passing_data() -> pd.DataFrame:
    """Load passing data from CSV, falling back to mock data if unavailable."""
    if PASSING_CSV.exists():
        df = pd.read_csv(PASSING_CSV)
        df = df.dropna(subset=["Player"])
        df = df[df["Player"].str.strip().str.len() > 0]

        df = df.rename(columns={"Player": "Passer"})
        df["Receiver"] = df["Passer"].shift(-1)
        df = df.dropna(subset=["Receiver"])
        print(f"Loaded {len(df)} rows from {PASSING_CSV.name}")
        return df

    print("[INFO] No CSV found, using mock data")
    return pd.DataFrame(
        [
            {"Passer": "Onana", "Receiver": "Martinez"},
            {"Passer": "Onana", "Receiver": "Dalot"},
            {"Passer": "Martinez", "Receiver": "Bruno Fernandes"},
            {"Passer": "Martinez", "Receiver": "Mainoo"},
            {"Passer": "Dalot", "Receiver": "Bruno Fernandes"},
            {"Passer": "Mainoo", "Receiver": "Bruno Fernandes"},
            {"Passer": "Bruno Fernandes", "Receiver": "Garnacho"},
            {"Passer": "Bruno Fernandes", "Receiver": "Garnacho"},
            {"Passer": "Bruno Fernandes", "Receiver": "Hojlund"},
            {"Passer": "Garnacho", "Receiver": "Hojlund"},
        ]
    )


def build_graph(data: pd.DataFrame) -> nx.DiGraph:
    """Extrae las conexiones dirigidas de Pases y crea el Grafo Matemático."""
    G = nx.DiGraph()

    for _, row in data.iterrows():
        source = row["Passer"]
        target = row["Receiver"]

        if G.has_edge(source, target):
            G[source][target]["weight"] += 1
        else:
            G.add_edge(source, target, weight=1)

    return G


def analyze_and_visualize(G: nx.DiGraph, output_filename="grafo_tactico.html"):
    """
    Calcula Betweenness Centrality y renderiza el mapa en HTML interactivo.
    """
    centrality = nx.betweenness_centrality(G, weight="weight")

    net = Network(
        height="600px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        directed=True,
    )

    for node in G.nodes():
        size = centrality.get(node, 0.01) * 200 + 10
        net.add_node(
            node,
            label=node,
            title=f"Betweenness: {centrality.get(node, 0.01):.2f}",
            size=size,
        )

    for source, target, data_edge in G.edges(data=True):
        weight = data_edge["weight"]
        net.add_edge(source, target, value=weight, title=f"{weight} pases")

    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", output_filename)
    net.write_html(out_path)
    print(f"Grafo interactivo renderizado con éxito en: {out_path}")


if __name__ == "__main__":
    df = load_passing_data()
    grafo = build_graph(df)
    analyze_and_visualize(grafo)
