"""
Tests for Graph Builder.
"""

import pytest

from src.graph import LayerNode, Edge, NeuroScopeGraph


class TestGraph:
    """Test suite for graph data structures."""

    def test_layer_node_display_type(self):
        """Grouped node should show combined types."""
        node = LayerNode(
            id=0,
            name="conv1",
            op_type="Conv",
            category="convolution",
            is_grouped=True,
            grouped_types=["Conv2d", "BatchNorm2d", "ReLU"],
        )
        assert node.display_type == "Conv2d + BatchNorm2d + ReLU"

    def test_layer_node_formatted_params(self):
        """Params should format correctly."""
        node1 = LayerNode(id=0, name="a", op_type="X", category="x", params=500)
        assert node1.formatted_params == "500"

        node2 = LayerNode(id=1, name="b", op_type="X", category="x", params=15000)
        assert node2.formatted_params == "15.0K"

        node3 = LayerNode(id=2, name="c", op_type="X", category="x", params=2500000)
        assert node3.formatted_params == "2.50M"

    def test_graph_compute_aggregates(self):
        """Graph should compute totals from nodes."""
        nodes = [
            LayerNode(id=0, name="a", op_type="X", category="x", params=100, flops=1000, memory_bytes=400),
            LayerNode(id=1, name="b", op_type="X", category="x", params=200, flops=2000, memory_bytes=800),
        ]
        graph = NeuroScopeGraph(nodes=nodes)
        graph.compute_aggregates()

        assert graph.total_params == 300
        assert graph.total_flops == 3000
        assert graph.total_memory_bytes == 1200

    def test_graph_health_score(self):
        """Health score should decrease with findings."""
        from src.graph import Finding, AnalysisReport

        report = AnalysisReport()
        report.findings = [
            Finding(severity="CRITICAL", rule_id="X", title="X", message="X", fix="X"),
            Finding(severity="WARNING", rule_id="Y", title="Y", message="Y", fix="Y"),
        ]
        report.compute_summary()

        assert report.health_score == 80  # 100 - 15 - 5
        assert report.health_grade == "B"
