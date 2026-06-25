"""
Compare API Route — Side-by-side model comparison.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.graph import AnalysisReport, NeuroScopeGraph
from src.analysis import AnalysisEngine
from src.analysis.flops import calculate_flops
from src.analysis.memory import estimate_memory
from src.store import graph_store

router = APIRouter()

analysis_engine = AnalysisEngine()


class CompareRequest(BaseModel):
    model_id_1: str
    model_id_2: str


class ModelSummary(BaseModel):
    model_name: str
    framework: str
    num_layers: int
    total_params: int
    total_flops: int
    total_memory_mb: float
    architecture_type: str
    health_score: int
    health_grade: str
    critical_count: int
    warning_count: int
    info_count: int


class ComparisonDelta(BaseModel):
    param_diff: int
    param_ratio: float
    flops_diff: int
    flops_ratio: float
    memory_diff_mb: float
    memory_ratio: float
    layer_diff: int
    health_score_diff: int


class CompareResponse(BaseModel):
    success: bool
    model_1: ModelSummary
    model_2: ModelSummary
    comparison: ComparisonDelta
    message: str


def _build_model_summary(graph: NeuroScopeGraph) -> ModelSummary:
    """
    Build a summary for one model by running analysis.

    Args:
        graph: The model graph.

    Returns:
        ModelSummary with stats and health info.
    """
    calculate_flops(graph)
    report = analysis_engine.analyze(graph)
    mem = estimate_memory(graph)

    return ModelSummary(
        model_name=graph.model_name,
        framework=graph.framework,
        num_layers=len(graph.nodes),
        total_params=graph.total_params,
        total_flops=graph.total_flops,
        total_memory_mb=round(mem["total_mb"], 2),
        architecture_type=graph.architecture_type,
        health_score=report.health_score,
        health_grade=report.health_grade,
        critical_count=report.critical_count,
        warning_count=report.warning_count,
        info_count=report.info_count,
    )


def _safe_ratio(a: float, b: float) -> float:
    """Compute ratio safely, avoiding division by zero."""
    if b == 0:
        return float("inf") if a > 0 else 0.0
    return round(a / b, 2)


@router.post("/compare", response_model=CompareResponse)
async def compare_models(request: CompareRequest):
    """
    Compare two models side by side.

    Accepts two model IDs (from prior uploads) and returns:
    - Per-model summaries (params, FLOPs, memory, health)
    - Deltas and ratios for comparison

    Args:
        request: Contains model_id_1 and model_id_2.

    Returns:
        CompareResponse with both summaries and comparison deltas.

    Raises:
        HTTPException 404: If either model is not found.
    """
    graph1 = graph_store.get(request.model_id_1)
    if not graph1:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {request.model_id_1}. Upload it first.",
        )

    graph2 = graph_store.get(request.model_id_2)
    if not graph2:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {request.model_id_2}. Upload it first.",
        )

    # Build summaries (each triggers its own analysis)
    summary1 = _build_model_summary(graph1)
    summary2 = _build_model_summary(graph2)

    # Compute comparison deltas
    comparison = ComparisonDelta(
        param_diff=summary2.total_params - summary1.total_params,
        param_ratio=_safe_ratio(summary2.total_params, summary1.total_params),
        flops_diff=summary2.total_flops - summary1.total_flops,
        flops_ratio=_safe_ratio(summary2.total_flops, summary1.total_flops),
        memory_diff_mb=round(summary2.total_memory_mb - summary1.total_memory_mb, 2),
        memory_ratio=_safe_ratio(summary2.total_memory_mb, summary1.total_memory_mb),
        layer_diff=summary2.num_layers - summary1.num_layers,
        health_score_diff=summary2.health_score - summary1.health_score,
    )

    return CompareResponse(
        success=True,
        model_1=summary1,
        model_2=summary2,
        comparison=comparison,
        message=f"Compared '{summary1.model_name}' vs '{summary2.model_name}'",
    )
