"""
Analysis Engine — The core differentiator of NeuroScope.

Runs a rules engine against a NeuroScopeGraph to detect:
- Layer-level anti-patterns
- Architecture-level issues
- Efficiency problems
- Task-specific mistakes

Also computes:
- FLOPs per layer and total
- Memory footprint
- Training time estimates
"""

from src.graph import AnalysisReport, Finding, NeuroScopeGraph
from src.analysis.rules.layer_rules import LayerRules
from src.analysis.rules.architecture_rules import ArchitectureRules
from src.analysis.rules.efficiency_rules import EfficiencyRules


# Op types for architecture detection
_RECURRENT_OPS = {"LSTM", "GRU", "RNN"}
_ATTENTION_OPS = {"Attention", "MultiHeadAttention"}
_CONV_OPS = {"Conv", "ConvTranspose", "QLinearConv"}
_POOLING_OPS = {"MaxPool", "AveragePool", "GlobalAveragePool", "GlobalMaxPool"}
_LINEAR_OPS = {"MatMul", "Gemm", "FC", "Linear"}


def detect_architecture_type(graph: NeuroScopeGraph) -> str:
    """
    Detect the architecture type from the graph structure.

    Examines the mix of operation types to classify the model.

    Args:
        graph: The parsed model graph.

    Returns:
        One of: "Transformer", "RNN", "CNN", "MLP", "GAN", "unknown".
    """
    op_counts: dict[str, int] = {}
    for node in graph.nodes:
        op_counts[node.op_type] = op_counts.get(node.op_type, 0) + 1

    has_attention = any(op in _ATTENTION_OPS for op in op_counts)
    has_recurrent = any(op in _RECURRENT_OPS for op in op_counts)
    has_conv = any(op in _CONV_OPS for op in op_counts)
    has_pooling = any(op in _POOLING_OPS for op in op_counts)
    has_linear = any(op in _LINEAR_OPS for op in op_counts)

    # Transformer: attention + linear, possibly with normalization
    if has_attention:
        return "Transformer"

    # RNN: recurrent ops
    if has_recurrent:
        if has_linear and not has_conv:
            return "RNN"
        return "RNN"

    # CNN: conv + pooling
    if has_conv and has_pooling:
        return "CNN"

    # Pure conv (no pooling, still CNN-like)
    if has_conv:
        return "CNN"

    # MLP: only linear + activation
    if has_linear and not has_conv and not has_recurrent:
        return "MLP"

    return "unknown"


class AnalysisEngine:
    """
    Orchestrates all analysis rules against a model graph.

    Usage:
        engine = AnalysisEngine()
        report = engine.analyze(graph)
        print(report.health_grade)  # "A", "B", "C", "D", "F"
    """

    def __init__(self):
        self.layer_rules = LayerRules()
        self.architecture_rules = ArchitectureRules()
        self.efficiency_rules = EfficiencyRules()

    def analyze(self, graph: NeuroScopeGraph) -> AnalysisReport:
        """
        Run full analysis on a model graph.

        Args:
            graph: The parsed model graph.

        Returns:
            AnalysisReport with findings, stats, and health score.
        """
        findings = []

        # Run all rule sets
        findings.extend(self.layer_rules.check(graph))
        findings.extend(self.architecture_rules.check(graph))
        findings.extend(self.efficiency_rules.check(graph))

        # Detect architecture type
        arch_type = detect_architecture_type(graph)
        graph.architecture_type = arch_type

        # Compute stats
        graph.compute_aggregates()

        # Build report
        report = AnalysisReport(
            findings=findings,
            total_params=graph.total_params,
            total_flops=graph.total_flops,
            total_memory_bytes=graph.total_memory_bytes,
            num_layers=len(graph.nodes),
            architecture_type=graph.architecture_type,
        )
        report.compute_summary()

        return report
