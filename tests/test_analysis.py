"""Smoke tests for tactical-narrative-graph-analysis."""


def test_imports():
    from src.benchmark_sota import run_benchmark
    from src.generate_tables import generate
    from src.graph_analysis import run_graph_analysis
    from src.statistical_tests import run_statistical_tests

    assert callable(run_graph_analysis)
    assert callable(run_benchmark)
    assert callable(run_statistical_tests)
    assert callable(generate)
