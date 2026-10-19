"""Tests for export_visualizations module (per-team exports)."""

import networkx as nx
import pandas as pd

from src.export_visualizations import (
    export_dw_centralidad,
    export_flourish_arc,
    export_observable_grafo,
)


def _tiny_graph() -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_edge("A", "B", weight=5)
    G.add_edge("B", "C", weight=3)
    G.add_edge("A", "C", weight=2)
    return G


def test_export_flourish_arc_writes_edges(tmp_path):
    out = tmp_path / "flourish_arc_diagram_alpha.csv"
    export_flourish_arc(_tiny_graph(), out)
    df = pd.read_csv(out)
    assert set(df.columns) >= {"source", "target", "weight"}
    assert len(df) == 3


def test_export_observable_grafo_writes_nodes(tmp_path):
    out = tmp_path / "observable_grafo_alpha.csv"
    export_observable_grafo(_tiny_graph(), out)
    df = pd.read_csv(out)
    assert set(df.columns) >= {"node", "betweenness"}
    assert len(df) == 3


def test_export_dw_centralidad_writes_roles(tmp_path):
    out = tmp_path / "dw_centralidad_alpha.csv"
    export_dw_centralidad(_tiny_graph(), out)
    df = pd.read_csv(out)
    assert set(df.columns) >= {"player", "betweenness", "tactical_role"}
    assert len(df) == 3
