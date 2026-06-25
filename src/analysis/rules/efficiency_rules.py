"""
Efficiency Anti-Pattern Detection Rules.

These rules check for computational inefficiencies:
- Redundant layers
- Large kernel inefficiency
- Inefficient layer sequences
"""

from src.graph import Finding, NeuroScopeGraph


CONV_OPS = {"Conv", "ConvTranspose"}
POOLING_OPS = {"MaxPool", "AveragePool", "GlobalAveragePool", "GlobalMaxPool"}


class EfficiencyRules:
    """Efficiency anti-pattern detection rules."""

    def check(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Run all efficiency checks."""
        findings = []
        findings.extend(self._check_redundant_convs(graph))
        findings.extend(self._check_large_kernels(graph))
        findings.extend(self._check_no_pooling(graph))
        return findings

    def _check_redundant_convs(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check for consecutive identical conv layers without benefit."""
        findings = []

        for i in range(len(graph.nodes) - 1):
            current = graph.nodes[i]
            next_node = graph.nodes[i + 1]

            if (
                current.op_type in CONV_OPS
                and next_node.op_type in CONV_OPS
                and current.attributes.get("kernel_shape") == next_node.attributes.get("kernel_shape")
                and current.output_shapes == next_node.output_shapes
            ):
                findings.append(
                    Finding(
                        severity="INFO",
                        rule_id="EFF_001",
                        title="Potentially Redundant Conv Layers",
                        message=(
                            f"'{current.name}' and '{next_node.name}' have the same "
                            f"kernel shape and output dimensions. Two consecutive "
                            f"identical conv layers may be redundant unless combined "
                            f"with non-linearity between them."
                        ),
                        fix="Verify that an activation function exists between these "
                            f"layers. If so, this is a valid pattern (deeper features). "
                            f"If not, consider merging them.",
                        layer_ids=[current.id, next_node.id],
                        category="efficiency",
                    )
                )

        return findings

    def _check_large_kernels(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check for unnecessarily large kernels."""
        findings = []

        for node in graph.nodes:
            if node.op_type in CONV_OPS:
                kernel = node.attributes.get("kernel_shape", [])
                if isinstance(kernel, list) and len(kernel) >= 2:
                    if kernel[0] > 7 or kernel[1] > 7:
                        findings.append(
                            Finding(
                                severity="WARNING",
                                rule_id="EFF_002",
                                title="Large Kernel Size",
                                message=(
                                    f"'{node.name}' uses a {kernel[0]}x{kernel[1]} kernel. "
                                    f"Large kernels are computationally expensive. "
                                    f"Multiple smaller kernels (e.g., two 3x3 instead of "
                                    f"one 7x7) can achieve similar receptive field with "
                                    f"fewer parameters."
                                ),
                                fix="Consider using stacked 3x3 kernels instead, or "
                                    f"depthwise separable convolutions.",
                                layer_ids=[node.id],
                                category="efficiency",
                            )
                        )

        return findings

    def _check_no_pooling(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check for conv networks without pooling layers."""
        findings = []

        conv_count = sum(1 for n in graph.nodes if n.op_type in CONV_OPS)
        pool_count = sum(1 for n in graph.nodes if n.op_type in POOLING_OPS)

        if conv_count > 3 and pool_count == 0:
            # Check if strided convolutions are used instead
            has_strided_conv = any(
                n.attributes.get("strides", [1]) != [1]
                for n in graph.nodes
                if n.op_type in CONV_OPS
            )

            if not has_strided_conv:
                findings.append(
                    Finding(
                        severity="WARNING",
                        rule_id="EFF_003",
                        title="No Pooling or Strided Convolutions",
                        message=(
                            f"Network has {conv_count} conv layers but no pooling "
                            f"layers or strided convolutions. Without spatial "
                            f"reduction, feature maps stay large throughout the "
                            f"network, wasting computation."
                        ),
                        fix="Add MaxPool or AveragePool layers between conv blocks, "
                            f"or use strided convolutions (stride=2) for downsampling.",
                        category="efficiency",
                    )
                )

        return findings
