"""
Tests for Analysis Rules.
"""

import pytest

from src.graph import LayerNode, Edge, NeuroScopeGraph, Finding
from src.analysis.rules.layer_rules import LayerRules
from src.analysis.rules.architecture_rules import ArchitectureRules
from src.analysis.rules.efficiency_rules import EfficiencyRules


def _make_node(id, op_type, category="other", params=0):
    """Helper to create a test node."""
    return LayerNode(
        id=id,
        name=f"layer_{id}",
        op_type=op_type,
        category=category,
        params=params,
    )


def _make_graph(nodes, edges=None):
    """Helper to create a test graph."""
    return NeuroScopeGraph(
        nodes=nodes,
        edges=edges or [],
    )


class TestLayerRules:
    """Test suite for layer-level rules."""

    def setup_method(self):
        self.rules = LayerRules()

    def test_missing_activation_detected(self):
        """Two linear layers without activation should trigger."""
        nodes = [
            _make_node(0, "MatMul", "linear"),
            _make_node(1, "MatMul", "linear"),
        ]
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert any(f.rule_id == "LAYER_001" for f in findings)

    def test_activation_between_linear_ok(self):
        """Linear + ReLU + Linear should NOT trigger missing activation."""
        nodes = [
            _make_node(0, "MatMul", "linear"),
            _make_node(1, "Relu", "activation"),
            _make_node(2, "MatMul", "linear"),
        ]
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert not any(f.rule_id == "LAYER_001" for f in findings)

    def test_sigmoid_in_deep_network(self):
        """Sigmoid in a deep network should trigger warning."""
        nodes = [_make_node(i, "Conv", "convolution") for i in range(10)]
        nodes.append(_make_node(10, "Sigmoid", "activation"))
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert any(f.rule_id == "LAYER_002" for f in findings)

    def test_no_batch_norm_in_deep_cnn(self):
        """Deep CNN without BN should trigger warning."""
        nodes = [_make_node(i, "Conv", "convolution") for i in range(8)]
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert any(f.rule_id == "LAYER_003" for f in findings)


class TestArchitectureRules:
    """Test suite for architecture-level rules."""

    def setup_method(self):
        self.rules = ArchitectureRules()

    def test_deep_network_without_skip_connections(self):
        """Deep network without skip connections should trigger."""
        nodes = [_make_node(i, "Conv", "convolution") for i in range(20)]
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert any(f.rule_id == "ARCH_001" for f in findings)

    def test_deep_network_with_skip_connections(self):
        """Deep network with skip connections should NOT trigger."""
        nodes = [_make_node(i, "Conv", "convolution") for i in range(20)]
        edges = [Edge(source_id=0, target_id=19, edge_type="residual")]
        graph = _make_graph(nodes, edges)
        findings = self.rules.check(graph)

        assert not any(f.rule_id == "ARCH_001" for f in findings)

    def test_large_fc_layer(self):
        """FC layer with >10M params should trigger."""
        nodes = [
            _make_node(0, "MatMul", "linear", params=15_000_000),
        ]
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert any(f.rule_id == "ARCH_002" for f in findings)

    def test_no_dropout(self):
        """Network with FC layers but no dropout should trigger."""
        nodes = [
            _make_node(0, "Conv", "convolution"),
            _make_node(1, "MatMul", "linear"),
        ]
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert any(f.rule_id == "ARCH_003" for f in findings)


class TestEfficiencyRules:
    """Test suite for efficiency rules."""

    def setup_method(self):
        self.rules = EfficiencyRules()

    def test_large_kernel_warning(self):
        """Conv with kernel >7 should trigger."""
        nodes = [
            LayerNode(
                id=0,
                name="conv1",
                op_type="Conv",
                category="convolution",
                attributes={"kernel_shape": [11, 11]},
            )
        ]
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert any(f.rule_id == "EFF_002" for f in findings)

    def test_no_pooling_warning(self):
        """Multiple convs without pooling should trigger."""
        nodes = [_make_node(i, "Conv", "convolution") for i in range(5)]
        graph = _make_graph(nodes)
        findings = self.rules.check(graph)

        assert any(f.rule_id == "EFF_003" for f in findings)
