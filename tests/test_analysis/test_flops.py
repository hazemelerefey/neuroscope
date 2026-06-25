"""
Tests for FLOPs Calculator.
"""

import pytest

from src.graph import LayerNode, NeuroScopeGraph
from src.analysis.flops import calculate_flops, _calculate_layer_flops


def _make_node(id, op_type, input_shapes=None, output_shapes=None, attributes=None):
    return LayerNode(
        id=id,
        name=f"layer_{id}",
        op_type=op_type,
        category="test",
        input_shapes=input_shapes or [],
        output_shapes=output_shapes or [],
        attributes=attributes or {},
    )


class TestFLOPsCalculator:
    """Test suite for FLOPs calculation."""

    def test_conv_flops(self):
        """Conv2d should have correct FLOPs."""
        node = _make_node(
            0, "Conv",
            input_shapes=[[1, 3, 224, 224]],
            output_shapes=[[1, 64, 112, 112]],
            attributes={"kernel_shape": [7, 7]},
        )
        flops = _calculate_layer_flops(node)
        # Expected: 1 × 64 × 112 × 112 × 2 × 3 × 7 × 7 = ~2,360,000,000
        assert flops > 0
        assert flops == 1 * 64 * 112 * 112 * 2 * 3 * 7 * 7

    def test_matmul_flops(self):
        """MatMul should have correct FLOPs."""
        node = _make_node(
            0, "MatMul",
            input_shapes=[[1, 512]],
            output_shapes=[[1, 256]],
        )
        flops = _calculate_layer_flops(node)
        # Expected: 2 × 1 × 1 × 512 × 256 = 262,144
        assert flops == 2 * 1 * 512 * 256

    def test_relu_flops(self):
        """ReLU should have FLOPs = output size."""
        node = _make_node(
            0, "Relu",
            input_shapes=[[1, 64, 112, 112]],
            output_shapes=[[1, 64, 112, 112]],
        )
        flops = _calculate_layer_flops(node)
        assert flops == 1 * 64 * 112 * 112

    def test_graph_total_flops(self):
        """Graph total FLOPs should be sum of all layers."""
        nodes = [
            _make_node(0, "Relu", output_shapes=[[1, 100]]),
            _make_node(1, "Relu", output_shapes=[[1, 100]]),
        ]
        graph = NeuroScopeGraph(nodes=nodes)
        calculate_flops(graph)

        assert graph.total_flops == 200  # 100 + 100
