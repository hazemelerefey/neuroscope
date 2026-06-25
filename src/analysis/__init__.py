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
