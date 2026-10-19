"""Tests for graph_builder module."""

import pandas as pd

from src.graph_builder import (
    analyze_teams,
    build_graph,
    build_team_graphs,
    load_passing_data,
)


def test_build_graph_creates_digraph():
    """Test that build_graph returns a DiGraph."""
    import networkx as nx

    df = pd.DataFrame(
        {
            "passer": ["A", "B", "A"],
            "receiver": ["B", "C", "C"],
            "weight": [5, 3, 2],
            "type": ["short", "medium", "long"],
        }
    )
    G = build_graph(df)
    assert isinstance(G, nx.DiGraph)
    assert len(G.nodes()) == 3
    assert len(G.edges()) == 3


def test_build_graph_aggregates_edges():
    """Test that multiple edges between same nodes are aggregated."""
    df = pd.DataFrame(
        {
            "passer": ["A", "A", "B"],
            "receiver": ["B", "B", "C"],
            "weight": [2, 3, 1],
        }
    )
    G = build_graph(df)
    assert G["A"]["B"]["weight"] == 5
    assert G["B"]["C"]["weight"] == 1


def test_build_graph_skips_self_loops():
    """Test that self-loops (passer == receiver) are skipped."""
    df = pd.DataFrame(
        {
            "passer": ["A", "A"],
            "receiver": ["A", "B"],
            "weight": [1, 2],
        }
    )
    G = build_graph(df)
    assert "A" in G.nodes()
    assert "B" in G.nodes()
    assert not G.has_edge("A", "A")
    assert G.has_edge("A", "B")


def test_build_graph_handles_legacy_columns():
    """Test build_graph handles legacy 'Passer'/'Receiver' columns."""
    df = pd.DataFrame(
        {
            "Passer": ["A", "B"],
            "Receiver": ["B", "C"],
            "weight": [1, 2],
        }
    )
    G = build_graph(df)
    assert len(G.nodes()) == 3
    assert G.has_edge("A", "B")


def test_build_graph_empty_dataframe():
    """Test build_graph with empty DataFrame."""
    df = pd.DataFrame({"passer": [], "receiver": [], "weight": []})
    G = build_graph(df)
    assert len(G.nodes()) == 0
    assert len(G.edges()) == 0


def test_load_passing_data_no_files(tmp_path, monkeypatch):
    """Test load_passing_data when no data files exist."""
    import src.graph_builder as gb_module

    monkeypatch.setattr(gb_module, "_get_data_dir", lambda: tmp_path)

    result = load_passing_data()
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_load_passing_data_with_passing_csv(tmp_path, monkeypatch):
    """Test load_passing_data with passing.csv fallback."""
    import src.graph_builder as gb_module

    monkeypatch.setattr(gb_module, "_get_data_dir", lambda: tmp_path)
    monkeypatch.setattr(
        gb_module, "_get_statsbomb_csv", lambda: tmp_path / "nonexistent.csv"
    )

    passing_csv = tmp_path / "passing.csv"
    pd.DataFrame(
        {
            "Player": ["Player A", "Player B", "Player C"],
            "Pos": ["GK", "DF", "MF"],
            "Cmp": [50, 40, 60],
            "PrgP": [5, 8, 12],
        }
    ).to_csv(passing_csv, index=False)

    result = load_passing_data()
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert "passer" in result.columns
    assert "receiver" in result.columns
    assert "weight" in result.columns


def _two_team_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "passer": ["A", "B", "X", "Y"],
            "receiver": ["B", "C", "Y", "Z"],
            "weight": [3, 2, 4, 1],
            "type": ["short", "short", "short", "long"],
            "team": ["Alpha", "Alpha", "Beta", "Beta"],
        }
    )


def test_load_passing_data_uses_completed_passes_only(tmp_path, monkeypatch):
    """Failed passes (Incomplete/Out/...) must not become edges."""
    import src.graph_builder as gb_module

    monkeypatch.setattr(gb_module, "_get_data_dir", lambda: tmp_path)

    pd.DataFrame(
        {
            "passer": ["A", "A", "A", "B"],
            "receiver": ["B", "B", "C", "C"],
            "team": ["Alpha", "Alpha", "Alpha", "Alpha"],
            "opponent": ["Beta", "Beta", "Beta", "Beta"],
            "pass_length": [5.0, 8.0, 12.0, 20.0],
            "pass_outcome": [None, "Incomplete", None, "Out"],
            "minute": [1, 2, 3, 4],
        }
    ).to_csv(tmp_path / "statsbomb_passes.csv", index=False)

    result = load_passing_data()

    assert set(result.columns) >= {
        "passer",
        "receiver",
        "weight",
        "attempted",
        "failed",
        "completion_rate",
    }

    edge_ab = result[(result["passer"] == "A") & (result["receiver"] == "B")].iloc[0]
    assert edge_ab["weight"] == 1  # completed only
    assert edge_ab["attempted"] == 2
    assert edge_ab["failed"] == 1
    assert edge_ab["completion_rate"] == 50.0

    # Pair with zero completed passes has no edge at all
    assert not ((result["passer"] == "B") & (result["receiver"] == "C")).any()

    edge_ac = result[(result["passer"] == "A") & (result["receiver"] == "C")].iloc[0]
    assert edge_ac["weight"] == 1
    assert edge_ac["failed"] == 0


def test_build_team_graphs_splits_by_team():
    """One DiGraph per team, no cross-team edges."""
    graphs = build_team_graphs(_two_team_df())
    assert set(graphs) == {"Alpha", "Beta"}

    alpha = graphs["Alpha"]
    assert set(alpha.nodes()) == {"A", "B", "C"}
    assert alpha["A"]["B"]["weight"] == 3

    beta = graphs["Beta"]
    assert set(beta.nodes()) == {"X", "Y", "Z"}
    assert beta["X"]["Y"]["weight"] == 4


def test_build_team_graphs_without_team_column():
    """Data without team column is treated as a single unnamed team."""
    df = pd.DataFrame(
        {
            "passer": ["A", "B"],
            "receiver": ["B", "C"],
            "weight": [1, 2],
        }
    )
    graphs = build_team_graphs(df)
    assert set(graphs) == {"unknown"}
    assert len(graphs["unknown"].nodes()) == 3


def test_build_team_graphs_empty_dataframe():
    assert build_team_graphs(pd.DataFrame()) == {}


def test_analyze_teams_writes_per_team_and_landing(tmp_path):
    """analyze_teams renders one HTML per team plus a landing page."""
    results = analyze_teams(data=_two_team_df(), output_dir=str(tmp_path))

    assert set(results) == {"Alpha", "Beta"}
    assert (tmp_path / "grafo_tactico_alpha.html").exists()
    assert (tmp_path / "grafo_tactico_beta.html").exists()

    landing = tmp_path / "grafo_tactico.html"
    assert landing.exists()
    content = landing.read_text(encoding="utf-8")
    assert "grafo_tactico_alpha.html" in content
    assert "grafo_tactico_beta.html" in content
