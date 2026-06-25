"""
Unified graph representation for NeuroScope.

All parsers (ONNX, PyTorch, Keras) produce this intermediate format,
which is then consumed by the analysis engine and 3D visualizer.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LayerNode:
    """Represents a single layer/operation in the neural network."""

    id: int
    name: str  # e.g., "features.0.conv1"
    op_type: str  # e.g., "Conv", "Relu", "MatMul"
    category: str  # e.g., "convolution", "activation", "linear"

    # Shapes
    input_shapes: list[list[int]] = field(default_factory=list)  # [[1, 3, 224, 224]]
    output_shapes: list[list[int]] = field(default_factory=list)  # [[1, 64, 112, 112]]

    # Attributes from the model (kernel_size, strides, etc.)
    attributes: dict = field(default_factory=dict)

    # Computed stats
    params: int = 0  # Number of trainable parameters
    flops: int = 0  # Floating-point operations
    memory_bytes: int = 0  # Memory footprint

    # Connections
    connections_in: list[int] = field(default_factory=list)  # Source node IDs
    connections_out: list[int] = field(default_factory=list)  # Target node IDs

    # Grouping (for merged patterns like Conv+BN+ReLU)
    is_grouped: bool = False
    grouped_types: list[str] = field(default_factory=list)

    # Educational description
    description: str = ""  # What this layer does (for students)

    @property
    def display_type(self) -> str:
        """Human-readable type name."""
        if self.is_grouped:
            return " + ".join(self.grouped_types)
        return self.op_type

    @property
    def formatted_params(self) -> str:
        """Human-readable parameter count."""
        if self.params < 1_000:
            return str(self.params)
        elif self.params < 1_000_000:
            return f"{self.params / 1_000:.1f}K"
        else:
            return f"{self.params / 1_000_000:.2f}M"


@dataclass
class Edge:
    """Represents a connection between two layer nodes."""

    source_id: int
    target_id: int
    edge_type: str = "sequential"  # sequential, skip, residual, concat
    label: Optional[str] = None


@dataclass
class Finding:
    """Represents an analysis finding (warning/error/info)."""

    severity: str  # "CRITICAL", "WARNING", "INFO"
    rule_id: str  # e.g., "LAYER_001"
    title: str  # Short title
    message: str  # Detailed explanation
    fix: str  # Suggested fix
    layer_ids: list[int] = field(default_factory=list)  # Affected layers
    category: str = ""  # "layer", "architecture", "efficiency", "task"

    @property
    def icon(self) -> str:
        return {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🟢"}.get(
            self.severity, "⚪"
        )


@dataclass
class AnalysisReport:
    """Complete analysis report for a model."""

    findings: list[Finding] = field(default_factory=list)

    # Stats
    total_params: int = 0
    total_flops: int = 0
    total_memory_bytes: int = 0
    num_layers: int = 0
    architecture_type: str = "unknown"  # CNN, Transformer, RNN, etc.

    # Estimates
    estimated_training_time_hours: float = 0.0
    estimated_gpu_memory_gb: float = 0.0

    # Summary
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0

    def compute_summary(self):
        """Compute summary counts from findings."""
        self.critical_count = sum(1 for f in self.findings if f.severity == "CRITICAL")
        self.warning_count = sum(1 for f in self.findings if f.severity == "WARNING")
        self.info_count = sum(1 for f in self.findings if f.severity == "INFO")

    @property
    def health_score(self) -> int:
        """Overall model health score (0-100)."""
        score = 100
        score -= self.critical_count * 15
        score -= self.warning_count * 5
        score -= self.info_count * 1
        return max(0, min(100, score))

    @property
    def health_grade(self) -> str:
        """Letter grade for model health."""
        score = self.health_score
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


@dataclass
class NeuroScopeGraph:
    """Complete graph representation of a neural network."""

    nodes: list[LayerNode] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    # Model metadata
    model_name: str = ""
    framework: str = ""  # "onnx", "pytorch", "keras"
    input_shapes: list[list[int]] = field(default_factory=list)
    output_shapes: list[list[int]] = field(default_factory=list)

    # Aggregate stats
    total_params: int = 0
    total_flops: int = 0
    total_memory_bytes: int = 0

    # Classification
    architecture_type: str = "unknown"  # CNN, Transformer, RNN, GAN, etc.

    def compute_aggregates(self):
        """Compute total stats from all nodes."""
        self.total_params = sum(n.params for n in self.nodes)
        self.total_flops = sum(n.flops for n in self.nodes)
        self.total_memory_bytes = sum(n.memory_bytes for n in self.nodes)

    def get_node_by_id(self, node_id: int) -> Optional[LayerNode]:
        """Get a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_connections(self, node_id: int) -> list[Edge]:
        """Get all edges involving a node."""
        return [
            e for e in self.edges
            if e.source_id == node_id or e.target_id == node_id
        ]
