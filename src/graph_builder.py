from __future__ import annotations

import json
import os
from pathlib import Path

import networkx as nx
import pandas as pd
from pyvis.network import Network

try:
    from .graph_analysis import compute_metrics
except ImportError:
    from graph_analysis import compute_metrics


def _get_data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "raw"


def _get_statsbomb_csv() -> Path:
    return _get_data_dir() / "statsbomb_passes.csv"


def _get_match_info_json() -> Path:
    return _get_data_dir() / "match_info.json"


def _is_completed_pass(outcomes: pd.Series) -> pd.Series:
    """Mask of completed passes: no outcome (NaN) or explicit 'Complete'."""
    return outcomes.isna() | outcomes.astype(str).str.lower().eq("complete")


def load_passing_data() -> pd.DataFrame:
    """Load real passing event data from StatsBomb Open Data.

    Uses event-level pass data with actual player names, pass locations,
    and pass outcomes. Each edge represents COMPLETED passes between two
    players; failed passes (Incomplete/Out/Pass Offside/Unknown) are
    excluded from the graph but kept as ``failed``/``attempted`` stats.

    Returns:
        DataFrame with columns: passer, receiver, weight (completed passes),
        attempted, failed, completion_rate, type, and metadata
    """
    statsbomb_csv = _get_statsbomb_csv()
    if statsbomb_csv.exists():
        print(f"[INFO] Loading real StatsBomb data from {statsbomb_csv.name}")
        df = pd.read_csv(statsbomb_csv)

        group_keys = ["passer", "receiver", "team", "opponent"]
        attempted = df.groupby(group_keys).size().rename("attempted")

        # Only completed passes become graph edges
        completed = df[_is_completed_pass(df["pass_outcome"])]
        edges = (
            completed.groupby(group_keys)
            .agg(
                weight=("passer", "size"),
                avg_length=("pass_length", "mean"),
                total_length=("pass_length", "sum"),
                first_minute=("minute", "min"),
                last_minute=("minute", "max"),
            )
            .reset_index()
            .merge(attempted, on=group_keys)
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

        edges["failed"] = edges["attempted"] - edges["weight"]
        edges["completion_rate"] = edges["weight"] / edges["attempted"] * 100

        print(f"[INFO] Built {len(edges)} passing edges (completed passes only)")
        print(
            f"[INFO] Completed passes: {int(edges['weight'].sum())} of {len(df)} "
            f"({len(df) - int(edges['weight'].sum())} failed excluded)"
        )

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

    else:
        print(f"[WARN] No StatsBomb event data found at {statsbomb_csv}")
        return pd.DataFrame()


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


def build_team_graphs(data: pd.DataFrame) -> dict[str, nx.DiGraph]:
    """Build one directed graph per team from the passing edge data.

    Each team gets its own DiGraph so that centrality, PageRank and
    communities are never computed on a mixture of both teams' passes.
    If the data has no ``team`` column it is treated as a single
    unnamed team.
    """
    if data.empty:
        return {}

    if "team" not in data.columns:
        return {"unknown": build_graph(data)}

    graphs = {
        str(team): build_graph(team_df)
        for team, team_df in data.groupby("team", sort=True)
    }
    return {team: G for team, G in graphs.items() if len(G.nodes) > 0}


def _team_slug(team: str) -> str:
    """Filesystem-safe slug for a team name."""
    return team.lower().replace(" ", "_")


def analyze_and_visualize(
    G: nx.DiGraph, output_filename="grafo_tactico.html", output_dir="output"
):
    """Calculate centrality metrics and render interactive visualization.

    Node size = betweenness centrality (higher = more important connector)
    Edge thickness = pass frequency (more passes = thicker line)

    Betweenness is reported in two flavors: unweighted (node size; each pass
    hop counts 1) and weighted with distance = 1/weight (frequent pass lanes
    become "short"). NetworkX treats ``weight`` as distance, so raw pass
    frequency would invert meaning; PageRank and degree stay weighted with
    frequency (frequency = importance there).
    """
    if len(G.nodes) == 0:
        print("[ERROR] Empty graph, nothing to visualize")
        return None

    metrics = compute_metrics(G)
    centrality = metrics["betweenness"]
    centrality_weighted = metrics["betweenness_weighted"]
    pagerank = metrics["pagerank"]
    in_degree = metrics["in_degree"]
    out_degree = metrics["out_degree"]

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
        bc_w = centrality_weighted.get(node, 0.0)
        pr = pagerank.get(node, 0.01)
        size = bc * 200 + 10
        title = (
            f"<b>{node}</b><br>"
            f"Betweenness (sin pesos): {bc:.3f}<br>"
            f"Betweenness (dist=1/pases): {bc_w:.3f}<br>"
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

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, output_filename)
    net.write_html(out_path)
    print(f"[INFO] Interactive graph saved to: {out_path}")
    return {
        "nodes": len(G.nodes),
        "edges": len(G.edges),
        "centrality": centrality,
        "pagerank": pagerank,
        "metrics": metrics,
    }


def _write_landing_page(
    output_dir: str, team_files: list[tuple[str, str]], match_label: str = ""
) -> str:
    """Write a landing page that embeds every per-team interactive graph."""
    sections = "\n".join(
        f"""    <section style="margin:24px 0;">
      <h2 style="font-family:sans-serif;color:#e94560;">{team}</h2>
      <iframe src="{fname}" title="Grafo táctico {team}"
        style="width:100%;height:720px;border:1px solid #533483;border-radius:8px;"></iframe>
    </section>"""
        for team, fname in team_files
    )
    match_line = (
        f'<p style="font-family:sans-serif;color:#bbb;">{match_label}</p>'
        if match_label
        else ""
    )
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Grafo táctico de pases, por equipo</title>
</head>
<body style="background:#1a1a2e;color:#eee;margin:0;padding:16px;">
  <h1 style="font-family:sans-serif;color:#fff;">Grafo táctico de pases (por equipo)</h1>
{match_line}
  <p style="font-family:sans-serif;color:#bbb;">Un grafo dirigido por equipo: nodos = jugadores, aristas = pases completados, grosor = frecuencia, tamaño del nodo = betweenness.</p>
{sections}
</body>
</html>
"""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "grafo_tactico.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] Landing page saved to: {out_path}")
    return out_path


def analyze_teams(
    data: pd.DataFrame | None = None, output_dir: str = "output"
) -> dict[str, dict]:
    """Build, analyze and render one interactive graph per team.

    Also writes ``grafo_tactico.html`` as a landing page embedding all
    per-team graphs.
    """
    if data is None:
        data = load_passing_data()

    teams = build_team_graphs(data)
    if not teams:
        print("[ERROR] No team graphs to visualize")
        return {}

    results: dict[str, dict] = {}
    team_files: list[tuple[str, str]] = []

    for team, G in teams.items():
        fname = f"grafo_tactico_{_team_slug(team)}.html"
        team_files.append((team, fname))
        metrics = analyze_and_visualize(G, output_filename=fname, output_dir=output_dir)
        if metrics is not None:
            results[team] = metrics
            print(
                f"[INFO] {team}: {metrics['nodes']} jugadores, {metrics['edges']} aristas de pase"
            )

    match_label = ""
    match_info_json = _get_match_info_json()
    if match_info_json.exists():
        try:
            with open(match_info_json, encoding="utf-8") as f:
                info = json.load(f)
            match_label = (
                f"{info.get('home_team', '?')} vs {info.get('away_team', '?')}, "
                f"{info.get('competition', '?')} ({info.get('match_date', '?')})"
            )
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    _write_landing_page(output_dir, team_files, match_label=match_label)
    return results


if __name__ == "__main__":
    analyze_teams()
