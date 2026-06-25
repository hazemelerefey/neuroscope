"""
Architecture-Level Anti-Pattern Detection Rules.

These rules check the overall architecture for structural issues:
- Missing skip connections in deep networks
- Parameter explosion in fully connected layers
- Missing dropout in classification heads
- Dimension mismatches
"""

from src.graph import Finding, NeuroScopeGraph


LINEAR_OPS = {"MatMul", "Gemm", "FC", "Linear"}
CONV_OPS = {"Conv", "ConvTranspose"}
DROPOUT_OPS = {"Dropout"}


class ArchitectureRules:
    """Architecture-level anti-pattern detection rules."""

    def check(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Run all architecture-level checks."""
        findings = []
        findings.extend(self._check_skip_connections(graph))
        findings.extend(self._check_fc_parameter_explosion(graph))
        findings.extend(self._check_missing_dropout(graph))
        findings.extend(self._check_premature_flatten(graph))
        return findings

    def _check_skip_connections(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check if deep networks have skip/residual connections."""
        findings = []

        # Count significant layers (non-activation, non-utility)
        significant_layers = [
            n for n in graph.nodes
            if n.category not in ("activation", "utility", "reshape")
        ]

        # Check for skip/residual edges
        skip_edges = [
            e for e in graph.edges
            if e.edge_type in ("skip", "residual")
        ]

        if len(significant_layers) > 15 and len(skip_edges) == 0:
            findings.append(
                Finding(
                    severity="CRITICAL",
                    rule_id="ARCH_001",
                    title="Deep Network Without Skip Connections",
                    message=(
                        f"Network has {len(significant_layers)} significant layers "
                        f"but no skip/residual connections detected. Deep networks "
                        f"without skip connections suffer from vanishing gradients "
                        f"and degradation problem."
                    ),
                    fix="Add residual connections (like ResNet) or use a pre-designed "
                        f"architecture with built-in skip connections (ResNet, DenseNet, "
                        f"UNet, etc.).",
                    category="architecture",
                )
            )

        return findings

    def _check_fc_parameter_explosion(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check for unnecessarily large fully connected layers."""
        findings = []

        for node in graph.nodes:
            if node.op_type in LINEAR_OPS and node.params > 10_000_000:
                findings.append(
                    Finding(
                        severity="WARNING",
                        rule_id="ARCH_002",
                        title="Large Fully Connected Layer",
                        message=(
                            f"'{node.name}' has {node.params:,} parameters "
                            f"({node.params / 1_000_000:.1f}M). This may indicate "
                            f"an unnecessarily large FC layer that wastes memory "
                            f"and computation."
                        ),
                        fix="Consider reducing the number of neurons, using global "
                            f"average pooling before the classifier, or adding "
                            f"dimensionality reduction layers.",
                        layer_ids=[node.id],
                        category="architecture",
                    )
                )

        return findings

    def _check_missing_dropout(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check for missing dropout before the final classifier."""
        findings = []

        has_dropout = any(n.op_type in DROPOUT_OPS for n in graph.nodes)
        has_classifier = any(n.op_type in LINEAR_OPS for n in graph.nodes)

        if has_classifier and not has_dropout:
            findings.append(
                Finding(
                    severity="WARNING",
                    rule_id="ARCH_003",
                    title="No Dropout Detected",
                    message=(
                        f"Network has fully connected layers but no dropout. "
                        f"Dropout is a simple and effective regularization technique "
                        f"that prevents overfitting by randomly zeroing neurons "
                        f"during training."
                    ),
                    fix="Add Dropout layers (typically 0.2-0.5 rate) before or after "
                        f"fully connected layers, especially the final classifier.",
                    category="architecture",
                )
            )

        return findings

    def _check_premature_flatten(self, graph: NeuroScopeGraph) -> list[Finding]:
        """Check if flattening happens too early (before sufficient spatial reduction)."""
        findings = []

        for i, node in enumerate(graph.nodes):
            if node.op_type == "Flatten":
                # Check if there are conv layers after the flatten
                has_conv_after = any(
                    n.op_type in CONV_OPS for n in graph.nodes[i + 1:]
                )
                if has_conv_after:
                    findings.append(
                        Finding(
                            severity="WARNING",
                            rule_id="ARCH_004",
                            title="Premature Flattening",
                            message=(
                                f"'{node.name}' flattens the tensor, but there are "
                                f"convolutional layers after it. Conv layers work on "
                                f"spatial data — flattening before them destroys spatial "
                                f"information."
                            ),
                            fix="Move the flatten operation after all convolutional "
                                f"and pooling layers.",
                            layer_ids=[node.id],
                            category="architecture",
                        )
                    )

        return findings
