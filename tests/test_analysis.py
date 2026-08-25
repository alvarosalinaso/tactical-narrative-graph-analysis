"""Smoke tests for tactical-narrative-graph-analysis."""
import pytest


def test_imports():
    from src.graph_analysis import run_graph_analysis
    from src.benchmark_sota import run_benchmark
    from src.statistical_tests import run_statistical_tests
    from src.generate_tables import generate
    assert callable(run_graph_analysis)
    assert callable(run_benchmark)
    assert callable(run_statistical_tests)
    assert callable(generate)
