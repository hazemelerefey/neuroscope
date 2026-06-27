"""
Analyze API Route — Run architecture analysis on uploaded models.
"""

import re
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.graph import NeuroScopeGraph
from src.analysis import AnalysisEngine
from src.analysis.flops import calculate_flops
from src.analysis.memory import estimate_memory, estimate_training_time
from src.store import graph_store

router = APIRouter()

analysis_engine = AnalysisEngine()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# UUID validation pattern
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)


class AnalyzeRequest(BaseModel):
    model_id: str  # UUID from upload response

    def validate_model_id(self) -> str:
        """Validate model_id is a proper UUID."""
        if not UUID_PATTERN.match(self.model_id):
            raise ValueError("Invalid model_id format. Expected UUID.")
        return self.model_id


class FindingResponse(BaseModel):
    severity: str
    rule_id: str
    title: str
    message: str
    fix: str
    layer_ids: list[int]
    category: str
    icon: str


class AnalysisResponse(BaseModel):
    success: bool
    findings: list[FindingResponse]
    health_score: int
    health_grade: str
    critical_count: int
    warning_count: int
    info_count: int
    total_params: int
    total_flops: int
    total_memory_mb: float
    architecture_type: str
    memory_estimate: dict
    training_time_estimate: dict


@router.post("/analyze", response_model=AnalysisResponse)
@limiter.limit("30/minute")
async def analyze_model(request: Request, analyze_request: AnalyzeRequest):
    """
    Run architecture analysis on a previously uploaded model.

    Returns:
        - Findings (warnings, errors, info)
        - Health score (0-100) and grade (A-F)
        - FLOPs, memory, and training time estimates
    """
    # Validate model_id format
    try:
        analyze_request.validate_model_id()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    graph = graph_store.get(analyze_request.model_id)
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {analyze_request.model_id}. Upload it first."
        )

    # Calculate FLOPs
    calculate_flops(graph)

    # Run analysis
    report = analysis_engine.analyze(graph)

    # Memory estimate
    mem_estimate = estimate_memory(graph)

    # Training time estimate (default: T4 GPU, batch 32, 10k samples, 100 epochs)
    time_estimate = estimate_training_time(graph)

    return AnalysisResponse(
        success=True,
        findings=[
            FindingResponse(
                severity=f.severity,
                rule_id=f.rule_id,
                title=f.title,
                message=f.message,
                fix=f.fix,
                layer_ids=f.layer_ids,
                category=f.category,
                icon=f.icon,
            )
            for f in report.findings
        ],
        health_score=report.health_score,
        health_grade=report.health_grade,
        critical_count=report.critical_count,
        warning_count=report.warning_count,
        info_count=report.info_count,
        total_params=report.total_params,
        total_flops=report.total_flops,
        total_memory_mb=mem_estimate["total_mb"],
        architecture_type=report.architecture_type,
        memory_estimate=mem_estimate,
        training_time_estimate=time_estimate,
    )
