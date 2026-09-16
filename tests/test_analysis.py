"""Smoke tests for tactical-narrative-graph-analysis."""

import pandas as pd
import pytest


def test_imports():
    from src.benchmark_sota import run_benchmark
    from src.generate_tables import generate
    from src.graph_analysis import run_graph_analysis
    from src.graph_builder import build_graph, load_passing_data
    from src.statistical_tests import run_statistical_tests

    assert callable(run_graph_analysis)
    assert callable(run_benchmark)
    assert callable(run_statistical_tests)
    assert callable(generate)
    assert callable(load_passing_data)
    assert callable(build_graph)


def test_load_passing_data():
    from src.graph_builder import load_passing_data

    df = load_passing_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "passer" in df.columns or "Passer" in df.columns
    assert "receiver" in df.columns or "Receiver" in df.columns


def test_build_graph():
    from src.graph_builder import build_graph, load_passing_data

    df = load_passing_data()
    G = build_graph(df)
    assert len(G.nodes) > 0
    assert len(G.edges) > 0


def test_graph_analysis():
    from src.graph_analysis import run_graph_analysis
    from pathlib import Path

    results = run_graph_analysis()
    assert isinstance(results, dict)


def test_statistical_tests():
    from src.statistical_tests import run_statistical_tests

    results = run_statistical_tests()
    assert isinstance(results, dict)
