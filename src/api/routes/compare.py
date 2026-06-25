"""
Compare API Route — Side-by-side model comparison.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class CompareRequest(BaseModel):
    model_id_1: str
    model_id_2: str


class CompareResponse(BaseModel):
    success: bool
    message: str
    # TODO: Add comparison results


@router.post("/compare", response_model=CompareResponse)
async def compare_models(request: CompareRequest):
    """
    Compare two models side by side.

    Returns:
        - Architectural differences
        - Parameter count comparison
        - FLOPs comparison
        - Memory comparison
    """
    # TODO: Implement comparison logic
    return CompareResponse(
        success=False,
        message="Model comparison not yet implemented. Coming in Phase 3.",
    )
