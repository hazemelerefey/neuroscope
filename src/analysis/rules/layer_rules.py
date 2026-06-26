"""
Layer-Level Anti-Pattern Detection Rules.

These rules check individual layers for common mistakes:
- Missing activation functions
- Wrong activation choices
- Missing normalization
- Incorrect layer ordering
"""

from src.graph import Finding, NeuroScopeGraph


# Layer type sets for quick lookup
LINEAR_OPS = {"MatMul", "Gemm", "FC", "Linear"}
CONV_OPS = {"Conv", "ConvTranspose", "QLinearConv"}
ACTIVATION_OPS = {
    "Relu", "LeakyRelu", "Gelu", "Silu", "Sigmoid", "Tanh",
    "Softmax", "Elu", "Selu", "Mish", "Hardswish", "PRelu",
}
NORMALIZATION_OPS = {
    "BatchNormalization", "InstanceNormalization",
    "LayerNormalization", "GroupNormalization",
}
POOLING_OPS = {
    "MaxPool", "AveragePool", "GlobalAveragePool",
    "GlobalMaxPool", "AdaptiveAveragePool", "AdaptiveMaxPool",
}
SATURATING_ACTIVATIONS = {"Sigmoid", "Tanh"}


class LayerRules:
    """Layer-level anti-pattern detection rules."""

    def check(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Run all layer-level checks."""
        findings = []
        findings.extend(self._check_missing_activation(graph))
        findings.extend(self._check_sigmoid_in_deep_network(graph))
        findings.extend(self._check_batch_norm_placement(graph))
        findings.extend(self._check_activation_after_final_layer(graph))
        return findings

    def _check_missing_activation(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check for linear layers without activation between them."""
        findings = []
        nodes = graph.nodes

        for i in range(len(nodes) - 1):
            current = nodes[i]
            next_node = nodes[i + 1]

            # If current is linear/conv and next is also linear/conv (no activation between)
            if (
                current.op_type in LINEAR_OPS | CONV_OPS
                and next_node.op_type in LINEAR_OPS | CONV_OPS
            ):
                # Consecutive linear/conv layers without activation between them
                # means the network cannot learn non-linear decision boundaries
                findings.append(
                    Finding(
                        severity="CRITICAL",
                        rule_id="LAYER_001",
                        title="Missing Activation Function",
                        message=(
                            f"No activation between '{current.name}' ({current.op_type}) "
                            f"and '{next_node.name}' ({next_node.op_type}). "
                            f"Stacking linear layers without activation collapses to a "
                            f"single linear transformation — the network cannot learn "
                            f"non-linear decision boundaries."
                        ),
                        fix="Add ReLU, GELU, or SiLU activation between the layers.",
                        layer_ids=[current.id, next_node.id],
                        category="layer",
                    )
                )

        return findings

    def _check_sigmoid_in_deep_network(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check for sigmoid/tanh in networks deeper than ~5 layers."""
        findings = []

        # Count non-activation, non-utility layers
        depth = sum(
            1 for n in graph.nodes
            if n.category not in ("activation", "utility", "reshape")
        )

        if depth > 5:
            for node in graph.nodes:
                if node.op_type in SATURATING_ACTIVATIONS:
                    findings.append(
                        Finding(
                            severity="WARNING",
                            rule_id="LAYER_002",
                            title="Saturating Activation in Deep Network",
                            message=(
                                f"'{node.name}' uses {node.op_type} activation in a "
                                f"{depth}-layer network. Saturating activations "
                                f"(Sigmoid, Tanh) produce gradients near zero for large "
                                f"inputs, which compounds across layers and causes "
                                f"vanishing gradients."
                            ),
                            fix="Replace with ReLU, GELU, or SiLU for hidden layers. "
                                f"Keep Sigmoid/Tanh only in the output layer if needed.",
                            layer_ids=[node.id],
                            category="layer",
                        )
                    )

        return findings

    def _check_batch_norm_placement(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check for missing batch normalization in deep CNNs."""
        findings = []

        conv_count = sum(1 for n in graph.nodes if n.op_type in CONV_OPS)
        bn_count = sum(1 for n in graph.nodes if n.op_type in NORMALIZATION_OPS)

        if conv_count > 5 and bn_count == 0:
            findings.append(
                Finding(
                    severity="WARNING",
                    rule_id="LAYER_003",
                    title="No Normalization in Deep CNN",
                    message=(
                        f"Network has {conv_count} convolutional layers but no "
                        f"normalization layers. Batch normalization stabilizes training "
                        f"and allows higher learning rates."
                    ),
                    fix="Add BatchNormalization after each convolutional layer.",
                    category="layer",
                )
            )

        return findings

    def _check_activation_after_final_layer(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check if the final layer has an appropriate activation."""
        findings = []

        if not graph.nodes:
            return findings

        # Find the last linear/conv layer
        last_linear = None
        for node in reversed(graph.nodes):
            if node.op_type in LINEAR_OPS | CONV_OPS:
                last_linear = node
                break

        if last_linear:
            # Check if there's an activation after it
            has_activation_after = False
            found_linear = False
            for node in graph.nodes:
                if node.id == last_linear.id:
                    found_linear = True
                    continue
                if found_linear and node.op_type in ACTIVATION_OPS:
                    has_activation_after = True
                    break

            # For classification, Softmax should be at the end
            if not has_activation_after:
                findings.append(
                    Finding(
                        severity="INFO",
                        rule_id="LAYER_004",
                        title="No Activation After Final Layer",
                        message=(
                            f"The final layer '{last_linear.name}' has no activation "
                            f"function. This is fine if the loss function includes "
                            f"softmax (e.g., CrossEntropyLoss), but verify this is "
                            f"intentional."
                        ),
                        fix="If using CrossEntropyLoss, this is correct. Otherwise, "
                            f"add Softmax for classification or Sigmoid for multi-label.",
                        layer_ids=[last_linear.id],
                        category="layer",
                    )
                )

        return findings
