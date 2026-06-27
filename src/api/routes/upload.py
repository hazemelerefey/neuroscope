"""
Upload API Route — Handle model file uploads.
"""

import os
import tempfile
import uuid
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.parsers import get_all_parsers
from src.graph import NeuroScopeGraph
from src.store import graph_store

router = APIRouter()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
SUPPORTED_EXTENSIONS = {".onnx", ".pt", ".pth", ".h5", ".keras", ".tflite"}


def _get_parsers():
    """Get all available parsers (lazy to avoid import errors at module load)."""
    return get_all_parsers()


class UploadResponse(BaseModel):
    success: bool
    message: str
    model_id: str  # UUID for this upload
    model_name: str
    framework: str
    num_layers: int
    total_params: int
    graph_json: dict  # Serialized graph for frontend


@router.post("/upload", response_model=UploadResponse)
@limiter.limit("10/minute")
async def upload_model(request: Request, file: UploadFile = File(...)):
    """
    Upload a model file for analysis.

    Supported formats: .onnx, .pt, .pth, .h5, .keras, .tflite
    Max file size: 500MB
    """
    # Validate file extension
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # Read file content with size limit
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Generate unique model ID
    model_id = str(uuid.uuid4())

    # Save to temp file and parse
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # Parse the model
        graph = _parse_model(tmp_path)

        # Store graph with UUID as key
        graph_store.put(model_id, graph)

        # Serialize graph for frontend
        graph_json = _serialize_graph(graph)

        return UploadResponse(
            success=True,
            message=f"Successfully parsed {filename}",
            model_id=model_id,
            model_name=graph.model_name,
            framework=graph.framework,
            num_layers=len(graph.nodes),
            total_params=graph.total_params,
            graph_json=graph_json,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse model: {e}")
    finally:
        # Always clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Best effort cleanup


def _parse_model(file_path: str) -> NeuroScopeGraph:
    """Parse a model file using the appropriate parser."""
    for parser in _get_parsers():
        if parser.supports(file_path):
            return parser.parse(file_path)

    raise ValueError(f"No parser found for file: {file_path}")


def _serialize_graph(graph: NeuroScopeGraph) -> dict:
    """Serialize a NeuroScopeGraph to JSON-compatible dict."""
    return {
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
                "display_type": n.display_type,
                "formatted_params": n.formatted_params,
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
        "model_name": graph.model_name,
        "framework": graph.framework,
        "input_shapes": graph.input_shapes,
        "output_shapes": graph.output_shapes,
        "total_params": graph.total_params,
        "total_flops": graph.total_flops,
        "total_memory_bytes": graph.total_memory_bytes,
        "architecture_type": graph.architecture_type,
    }
