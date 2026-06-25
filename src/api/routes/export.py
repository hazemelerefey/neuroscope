"""
Export API Route — Generate downloadable files from model analysis.
"""

import io
import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.graph import NeuroScopeGraph
from src.analysis import AnalysisEngine
from src.analysis.flops import calculate_flops
from src.analysis.memory import estimate_memory
from src.store import graph_store

router = APIRouter()

analysis_engine = AnalysisEngine()


class ExportRequest(BaseModel):
    model_id: str
    format: str  # "json", "png", "summary"


def _get_graph(model_id: str) -> NeuroScopeGraph:
    """
    Retrieve a graph from the shared store.

    Args:
        model_id: The model identifier.

    Returns:
        NeuroScopeGraph.

    Raises:
        HTTPException 404: If model not found.
    """
    graph = graph_store.get(model_id)
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {model_id}. Upload it first.",
        )
    return graph


def _export_json(graph: NeuroScopeGraph) -> StreamingResponse:
    """
    Export the full graph as JSON.

    Includes nodes, edges, metadata, and analysis results.

    Args:
        graph: The model graph.

    Returns:
        StreamingResponse with JSON content.
    """
    calculate_flops(graph)
    report = analysis_engine.analyze(graph)
    mem = estimate_memory(graph)

    data = {
        "model_name": graph.model_name,
        "framework": graph.framework,
        "architecture_type": graph.architecture_type,
        "input_shapes": graph.input_shapes,
        "output_shapes": graph.output_shapes,
        "total_params": graph.total_params,
        "total_flops": graph.total_flops,
        "total_memory_bytes": graph.total_memory_bytes,
        "nodes": [
            {
                "id": n.id,
                "name": n.name,
                "op_type": n.op_type,
                "category": n.category,
                "input_shapes": n.input_shapes,
                "output_shapes": n.output_shapes,
                "attributes": n.attributes,
                "params": n.params,
                "flops": n.flops,
                "memory_bytes": n.memory_bytes,
                "connections_in": n.connections_in,
                "connections_out": n.connections_out,
                "is_grouped": n.is_grouped,
                "grouped_types": n.grouped_types,
                "description": n.description,
            }
            for n in graph.nodes
        ],
        "edges": [
            {
                "source_id": e.source_id,
                "target_id": e.target_id,
                "edge_type": e.edge_type,
                "label": e.label,
            }
            for e in graph.edges
        ],
        "analysis": {
            "health_score": report.health_score,
            "health_grade": report.health_grade,
            "critical_count": report.critical_count,
            "warning_count": report.warning_count,
            "info_count": report.info_count,
            "findings": [
                {
                    "severity": f.severity,
                    "rule_id": f.rule_id,
                    "title": f.title,
                    "message": f.message,
                    "fix": f.fix,
                    "layer_ids": f.layer_ids,
                    "category": f.category,
                }
                for f in report.findings
            ],
        },
        "memory_estimate": mem,
    }

    content = json.dumps(data, indent=2, default=str)
    filename = f"{graph.model_name}_export.json"

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _export_png(graph: NeuroScopeGraph) -> StreamingResponse:
    """
    Export a PNG visualization of the model graph using matplotlib.

    Args:
        graph: The model graph.

    Returns:
        StreamingResponse with PNG image.

    Raises:
        HTTPException 500: If matplotlib is not available.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="matplotlib is required for PNG export. Install with: pip install matplotlib",
        )

    # Category colors
    colors = {
        "convolution": "#4CAF50",
        "linear": "#2196F3",
        "activation": "#FF9800",
        "pooling": "#9C27B0",
        "normalization": "#00BCD4",
        "reshape": "#607D8B",
        "regularization": "#F44336",
        "recurrent": "#795548",
        "attention": "#E91E63",
        "combination": "#CDDC39",
        "embedding": "#3F51B5",
        "other": "#9E9E9E",
        "input": "#8BC34A",
        "utility": "#BDBDBD",
    }

    fig, ax = plt.subplots(figsize=(max(12, len(graph.nodes) * 0.8), 6))

    if not graph.nodes:
        ax.text(0.5, 0.5, "Empty model", ha="center", va="center", fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    else:
        n = len(graph.nodes)
        x_positions = list(range(n))
        y_center = 0.5

        # Draw nodes
        node_width = 0.6
        node_height = 0.3
        for i, node in enumerate(graph.nodes):
            color = colors.get(node.category, "#9E9E9E")
            rect = mpatches.FancyBboxPatch(
                (i - node_width / 2, y_center - node_height / 2),
                node_width,
                node_height,
                boxstyle="round,pad=0.02",
                facecolor=color,
                edgecolor="black",
                linewidth=0.5,
                alpha=0.85,
            )
            ax.add_patch(rect)

            # Node label (truncated)
            label = node.op_type[:8]
            ax.text(
                i, y_center, label,
                ha="center", va="center",
                fontsize=7, fontweight="bold", color="white",
            )

            # Layer name below
            ax.text(
                i, y_center - node_height / 2 - 0.05,
                node.name[:12],
                ha="center", va="top",
                fontsize=5, color="#333",
            )

        # Draw edges
        for edge in graph.edges:
            x_start = edge.source_id
            x_end = edge.target_id
            edge_color = "#666"
            if edge.edge_type == "residual":
                edge_color = "#F44336"
                # Draw arc above for residual connections
                mid_x = (x_start + x_end) / 2
                mid_y = y_center + node_height / 2 + 0.15
                ax.annotate(
                    "",
                    xy=(x_end, y_center + node_height / 2),
                    xytext=(x_start, y_center + node_height / 2),
                    arrowprops=dict(
                        arrowstyle="->",
                        color=edge_color,
                        connectionstyle=f"arc3,rad=0.3",
                        linewidth=1.0,
                    ),
                )
            else:
                ax.annotate(
                    "",
                    xy=(x_end - node_width / 2, y_center),
                    xytext=(x_start + node_width / 2, y_center),
                    arrowprops=dict(
                        arrowstyle="->",
                        color=edge_color,
                        linewidth=0.8,
                    ),
                )

        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(-0.2, 1.0)
        ax.set_aspect("equal")
        ax.axis("off")

    # Title
    ax.set_title(
        f"NeuroScope: {graph.model_name} ({graph.framework})",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )

    # Legend (top-right)
    used_categories = set(n.category for n in graph.nodes)
    legend_handles = [
        mpatches.Patch(color=colors.get(cat, "#9E9E9E"), label=cat)
        for cat in sorted(used_categories)
    ]
    if legend_handles:
        ax.legend(
            handles=legend_handles,
            loc="upper right",
            fontsize=6,
            framealpha=0.9,
        )

    plt.tight_layout()

    # Save to buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    filename = f"{graph.model_name}_graph.png"

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _export_summary(graph: NeuroScopeGraph) -> StreamingResponse:
    """
    Export a human-readable text summary of the model and its analysis.

    Args:
        graph: The model graph.

    Returns:
        StreamingResponse with plain text content.
    """
    calculate_flops(graph)
    report = analysis_engine.analyze(graph)
    mem = estimate_memory(graph)

    lines = [
        "=" * 60,
        f"  NeuroScope Model Analysis Report",
        "=" * 60,
        "",
        f"Model:         {graph.model_name}",
        f"Framework:     {graph.framework}",
        f"Architecture:  {graph.architecture_type}",
        "",
        "-" * 60,
        "  Summary Statistics",
        "-" * 60,
        f"Layers:        {len(graph.nodes)}",
        f"Parameters:    {graph.total_params:,}",
        f"FLOPs:         {graph.total_flops:,}",
        f"Memory:        {mem['total_mb']:.2f} MB",
        f"GPU Memory:    {mem['gpu_memory_gb']:.2f} GB (est.)",
        "",
        f"Health Score:  {report.health_score}/100 (Grade: {report.health_grade})",
        f"  Critical:    {report.critical_count}",
        f"  Warnings:    {report.warning_count}",
        f"  Info:        {report.info_count}",
        "",
    ]

    # Layer breakdown
    if graph.nodes:
        lines.append("-" * 60)
        lines.append("  Layer Details")
        lines.append("-" * 60)
        for node in graph.nodes:
            params_str = node.formatted_params
            lines.append(
                f"  [{node.id:3d}] {node.name:<30s} {node.op_type:<20s} "
                f"params={params_str}"
            )
        lines.append("")

    # Findings
    if report.findings:
        lines.append("-" * 60)
        lines.append("  Analysis Findings")
        lines.append("-" * 60)
        for f in report.findings:
            lines.append(f"  {f.icon} [{f.severity}] {f.title}")
            lines.append(f"     Rule: {f.rule_id}")
            lines.append(f"     {f.message}")
            lines.append(f"     Fix: {f.fix}")
            if f.layer_ids:
                lines.append(f"     Layers: {f.layer_ids}")
            lines.append("")

    lines.append("=" * 60)
    lines.append("  Generated by NeuroScope — AI-Powered 3D NN Visualizer")
    lines.append("=" * 60)

    content = "\n".join(lines)
    filename = f"{graph.model_name}_report.txt"

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/export")
async def export_model(request: ExportRequest):
    """
    Export model visualization or analysis report.

    Supported formats:
        - json: Full graph data with analysis results
        - png: Graph visualization rendered with matplotlib
        - summary: Human-readable text report

    Args:
        request: ExportRequest with model_id and format.

    Returns:
        StreamingResponse with the exported file.

    Raises:
        HTTPException 400: If format is unsupported.
        HTTPException 404: If model is not found.
    """
    graph = _get_graph(request.model_id)

    format_lower = request.format.lower()

    if format_lower == "json":
        return _export_json(graph)
    elif format_lower == "png":
        return _export_png(graph)
    elif format_lower == "summary":
        return _export_summary(graph)
    else:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported export format: '{request.format}'. "
                f"Available: json, png, summary"
            ),
        )
