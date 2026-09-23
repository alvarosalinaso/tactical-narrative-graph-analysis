from __future__ import annotations

import json
import os
from pathlib import Path

import networkx as nx
import pandas as pd
from pyvis.network import Network


def _get_data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "raw"


def _get_statsbomb_csv() -> Path:
    return _get_data_dir() / "statsbomb_passes.csv"


def _get_match_info_json() -> Path:
    return _get_data_dir() / "match_info.json"


def _get_passing_csv() -> Path:
    return _get_data_dir() / "passing.csv"


def load_passing_data() -> pd.DataFrame:
    """Load real passing event data from StatsBomb Open Data.

    Uses event-level pass data with actual player names, pass locations,
    and pass outcomes. Each edge represents a real pass between two players.

    Returns:
        DataFrame with columns: passer, receiver, weight, type, and metadata
    """
    statsbomb_csv = _get_statsbomb_csv()
    if statsbomb_csv.exists():
        print(f"[INFO] Loading real StatsBomb data from {statsbomb_csv.name}")
        df = pd.read_csv(statsbomb_csv)

        # Aggregate passes between same player pairs
        edges = (
            df.groupby(["passer", "receiver", "team", "opponent"])
            .agg(
                weight=("pass_length", "count"),
                avg_length=("pass_length", "mean"),
                total_length=("pass_length", "sum"),
                complete=("pass_outcome", lambda x: x.isna().sum()),
                incomplete=("pass_outcome", lambda x: x.notna().sum()),
                first_minute=("minute", "min"),
                last_minute=("minute", "max"),
            )
            .reset_index()
        )

        # Classify pass types based on length
        def classify_pass(row):
            if row["avg_length"] < 10:
                return "short"
            elif row["avg_length"] < 25:
                return "medium"
            else:
                return "long"

        edges["type"] = edges.apply(classify_pass, axis=1)

        # Calculate completion rate
        edges["completion_rate"] = edges["complete"] / edges["weight"] * 100

        print(f"[INFO] Built {len(edges)} real passing edges")
        print(f"[INFO] Total passes analyzed: {len(df)}")

        # Print match info if available
        match_info_json = _get_match_info_json()
        if match_info_json.exists():
            try:
                with open(match_info_json) as f:
                    info = json.load(f)
                print(
                    f"[INFO] Match: {info.get('home_team', '?')} vs {info.get('away_team', '?')}"
                )
                print(f"[INFO] Competition: {info.get('competition', '?')}")
            except (json.JSONDecodeError, KeyError):
                pass

        return edges

    elif _get_passing_csv().exists():
        print(f"[INFO] Falling back to aggregate stats from {_get_passing_csv().name}")
        return _load_aggregate_stats()

    else:
        print("[WARN] No data files found")
        return pd.DataFrame()


def _load_aggregate_stats() -> pd.DataFrame:
    """Load aggregate passing stats when event-level data is unavailable.

    ILLUSTRATIVE FALLBACK: builds synthetic positional edges from season
    aggregate stats (Cmp/PrgP), not observed pass events. Edge weights and
    any centrality derived from this graph are illustrative only and must
    not be compared against StatsBomb event-level results.
    """
    df = pd.read_csv(_get_passing_csv())
    df = df.dropna(subset=["Player"])
    df = df[df["Player"].str.strip().str.len() > 0]
    df = df[df["Player"].str.strip() != "Total"]

    if "Cmp" not in df.columns or "PrgP" not in df.columns:
        return pd.DataFrame()

    players = df[["Player", "Pos", "Cmp", "PrgP"]].copy()
    players["Cmp"] = pd.to_numeric(players["Cmp"], errors="coerce").fillna(0)
    players["PrgP"] = pd.to_numeric(players["PrgP"], errors="coerce").fillna(0)

    def classify_position(pos: str) -> str:
        pos_upper = pos.upper()
        if "GK" in pos_upper:
            return "GK"
        if "DF" in pos_upper:
            return "DF"
        if "MF" in pos_upper and "FW" not in pos_upper:
            return "MF"
        if "FW" in pos_upper:
            return "FW"
        return "MF"

    players["position"] = players["Pos"].apply(classify_position)

    edges = []
    gk = players[players["position"] == "GK"]
    df_players = players[players["position"] == "DF"]
    mf_players = players[players["position"] == "MF"]
    fw_players = players[players["position"] == "FW"]

    for _, g in gk.iterrows():
        for _, d in df_players.iterrows():
            weight = max(1, int(g["Cmp"] * 0.03))
            if weight > 0:
                edges.append(
                    {
                        "passer": g["Player"],
                        "receiver": d["Player"],
                        "weight": weight,
                        "type": "distribution",
                    }
                )

    for _, d in df_players.iterrows():
        for _, m in mf_players.iterrows():
            weight = max(1, int(d["Cmp"] * 0.02))
            if weight > 0:
                edges.append(
                    {
                        "passer": d["Player"],
                        "receiver": m["Player"],
                        "weight": weight,
                        "type": "buildup",
                    }
                )

    for _, m in mf_players.iterrows():
        for _, f in fw_players.iterrows():
            weight = max(1, int(m["Cmp"] * 0.03))
            if weight > 0:
                edges.append(
                    {
                        "passer": m["Player"],
                        "receiver": f["Player"],
                        "weight": weight,
                        "type": "final_ball",
                    }
                )

    return pd.DataFrame(edges)


def build_graph(data: pd.DataFrame) -> nx.DiGraph:
    """Build a directed graph from passing edge data.

    Supports both real StatsBomb data (lowercase columns) and legacy format.
    Node size is based on betweenness centrality.
    Edge weight represents number of passes between players.
    """
    G = nx.DiGraph()

    for _, row in data.iterrows():
        source = row.get("passer", row.get("Passer", ""))
        target = row.get("receiver", row.get("Receiver", ""))
        weight = row.get("weight", 1)

        if not source or not target or source == target:
            continue

        if G.has_edge(source, target):
            G[source][target]["weight"] += weight
        else:
            G.add_edge(source, target, weight=weight)

    return G


def analyze_and_visualize(G: nx.DiGraph, output_filename="grafo_tactico.html"):
    """Calculate centrality metrics and render interactive visualization.

    Node size = betweenness centrality (higher = more important connector)
    Edge thickness = pass frequency (more passes = thicker line)

    Betweenness is unweighted: NetworkX treats ``weight`` as distance, so a
    pass-frequency weight would invert meaning (frequent passes = long paths).
    PageRank and degree stay weighted (frequency = importance there).
    """
    if len(G.nodes) == 0:
        print("[ERROR] Empty graph, nothing to visualize")
        return

    centrality = nx.betweenness_centrality(G)
    pagerank = nx.pagerank(G, weight="weight")
    in_degree = dict(G.in_degree(weight="weight"))
    out_degree = dict(G.out_degree(weight="weight"))

    net = Network(
        height="700px",
        width="100%",
        bgcolor="#1a1a2e",
        font_color="white",
        directed=True,
        notebook=False,
        cdn_resources="remote",
    )

    for node in G.nodes():
        bc = centrality.get(node, 0.01)
        pr = pagerank.get(node, 0.01)
        size = bc * 200 + 10
        title = (
            f"<b>{node}</b><br>"
            f"Betweenness: {bc:.3f}<br>"
            f"PageRank: {pr:.3f}<br>"
            f"In: {in_degree.get(node, 0)} passes<br>"
            f"Out: {out_degree.get(node, 0)} passes"
        )
        net.add_node(
            node,
            label=node,
            title=title,
            size=size,
            color={"background": "#e94560", "border": "#0f3460"},
        )

    max_weight = max([d["weight"] for _, _, d in G.edges(data=True)], default=1)

    for source, target, data_edge in G.edges(data=True):
        weight = data_edge["weight"]
        width = max(1, (weight / max_weight) * 8)
        net.add_edge(
            source,
            target,
            value=width,
            title=f"{weight} passes",
            color={"color": "#533483", "highlight": "#e94560"},
        )

    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", output_filename)
    net.write_html(out_path)
    print(f"[INFO] Interactive graph saved to: {out_path}")
    return {
        "nodes": len(G.nodes),
        "edges": len(G.edges),
        "centrality": centrality,
        "pagerank": pagerank,
    }


if __name__ == "__main__":
    df = load_passing_data()
    grafo = build_graph(df)
    analyze_and_visualize(grafo)
