"""Tests for graph_analysis module."""

import csv
import json

import pandas as pd

from src.graph_analysis import build_graph_from_csv, run_graph_analysis


def test_build_graph_from_csv(tmp_path):
    """Test building graph from CSV."""
    csv_file = tmp_path / "test_passes.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "weight"])
        writer.writeheader()
        writer.writerow({"source": "A", "target": "B", "weight": "5"})
        writer.writerow({"source": "B", "target": "C", "weight": "3"})
        writer.writerow({"source": "A", "target": "C", "weight": "2"})

    import networkx as nx

    G = build_graph_from_csv(csv_file)
    assert isinstance(G, nx.DiGraph)
    assert len(G.nodes()) == 3
    assert len(G.edges()) == 3
    assert G["A"]["B"]["weight"] == 5


def test_run_graph_analysis_returns_dict(tmp_path, monkeypatch):
    """Test run_graph_analysis returns expected structure."""
    import src.graph_analysis as ga_module

    monkeypatch.setattr(ga_module, "NX_AVAILABLE", True)

    data_dir = tmp_path / "export"
    output_dir = tmp_path / "export_out"
    data_dir.mkdir()
    output_dir.mkdir()

    # Create a simple CSV
    csv_file = data_dir / "test_network.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "weight"])
        writer.writeheader()
        writer.writerow({"source": "A", "target": "B", "weight": "5"})
        writer.writerow({"source": "B", "target": "C", "weight": "3"})
        writer.writerow({"source": "A", "target": "C", "weight": "2"})
        writer.writerow({"source": "C", "target": "A", "weight": "1"})

    result = run_graph_analysis(data_dir=data_dir, output_dir=output_dir)
    assert isinstance(result, dict)
    assert "test_network" in result
    metrics = result["test_network"]
    assert "nodes" in metrics
    assert "edges" in metrics
    assert "density" in metrics
    assert "top_betweenness" in metrics
    assert "top_pagerank" in metrics
    assert "top_degree" in metrics


def test_run_graph_analysis_no_nx(tmp_path, monkeypatch):
    """Test run_graph_analysis when NetworkX not available."""
    import src.graph_analysis as ga_module

    monkeypatch.setattr(ga_module, "NX_AVAILABLE", False)

    data_dir = tmp_path / "export"
    output_dir = tmp_path / "export_out"
    data_dir.mkdir()
    output_dir.mkdir()

    result = run_graph_analysis(data_dir=data_dir, output_dir=output_dir)
    assert result == {}


def test_run_graph_analysis_no_csv(tmp_path, monkeypatch):
    """Test run_graph_analysis with no CSV files."""
    import src.graph_analysis as ga_module

    monkeypatch.setattr(ga_module, "NX_AVAILABLE", True)

    data_dir = tmp_path / "export"
    output_dir = tmp_path / "export_out"
    data_dir.mkdir()
    output_dir.mkdir()

    result = run_graph_analysis(data_dir=data_dir, output_dir=output_dir)
    assert result == {}


def test_run_graph_analysis_creates_output_files(tmp_path, monkeypatch):
    """Test run_graph_analysis creates output files."""
    import src.graph_analysis as ga_module

    monkeypatch.setattr(ga_module, "NX_AVAILABLE", True)

    data_dir = tmp_path / "export"
    output_dir = tmp_path / "export_out"
    data_dir.mkdir()
    output_dir.mkdir()

    csv_file = data_dir / "test_network.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "weight"])
        writer.writeheader()
        writer.writerow({"source": "A", "target": "B", "weight": "5"})
        writer.writerow({"source": "B", "target": "C", "weight": "3"})

    run_graph_analysis(data_dir=data_dir, output_dir=output_dir)

    # Check JSON output
    json_file = output_dir / "test_network_network_metrics.json"
    assert json_file.exists()
    with open(json_file) as f:
        content = json.load(f)
    assert content["nodes"] == 3

    # Check CSV output
    pr_csv = output_dir / "test_network_pagerank.csv"
    assert pr_csv.exists()
    pr_df = pd.read_csv(pr_csv)
    assert "player" in pr_df.columns
    assert "pagerank" in pr_df.columns
