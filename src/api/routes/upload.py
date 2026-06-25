"""
Upload API Route — Handle model file uploads.
"""

import os
import tempfile
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from src.parsers.onnx_parser import ONNXParser
from src.graph import NeuroScopeGraph
from src.api.routes.analyze import graph_store

router = APIRouter()

# Parser registry
PARSERS = [ONNXParser()]


class UploadResponse(BaseModel):
    success: bool
    message: str
    model_name: str
    framework: str
    num_layers: int
    total_params: int
    graph_json: dict  # Serialized graph for frontend


@router.post("/upload", response_model=UploadResponse)
async def upload_model(file: UploadFile = File(...)):
    """
    Upload a model file for analysis.

    Supported formats: .onnx, .pt, .pth, .h5, .keras, .tflite
    Max file size: 500MB
    """
    # Validate file extension
    filename = file.filename or ""
    supported_extensions = {".onnx", ".pt", ".pth", ".h5", ".keras", ".tflite"}
    ext = os.path.splitext(filename)[1].lower()

    if ext not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {ext}. Supported: {', '.join(supported_extensions)}"
        )

    # Save uploaded file to temp directory
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Parse the model
    try:
        graph = _parse_model(tmp_path)
    except Exception as e:
        os.unlink(tmp_path)
        raise HTTPException(status_code=422, detail=f"Failed to parse model: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Store graph in shared store for analyze/export routes
    graph_store[graph.model_name] = graph

    # Serialize graph for frontend
    graph_json = _serialize_graph(graph)

    return UploadResponse(
        success=True,
        message=f"Successfully parsed {filename}",
        model_name=graph.model_name,
        framework=graph.framework,
        num_layers=len(graph.nodes),
        total_params=graph.total_params,
        graph_json=graph_json,
    )


def _parse_model(file_path: str) -> NeuroScopeGraph:
    """Parse a model file using the appropriate parser."""
    for parser in PARSERS:
        if parser.supports(file_path):
            return parser.parse(file_path)

    # Try ONNX as fallback for unknown formats
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
