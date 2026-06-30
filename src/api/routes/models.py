"""
Models API Route — Serve model definitions for the visual builder.
"""

import json
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Path to model definitions
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "models"


class ModelFamily(BaseModel):
    id: str
    name: str
    description: str
    versions: list[str]


class LayerDefinition(BaseModel):
    id: str
    type: str
    name: str
    params: dict
    code: str
    freezable: bool


class ExtensionOption(BaseModel):
    id: str
    name: str
    code: str
    description: str
    when_to_use: str
    consequences: str
    default: bool


class Extension(BaseModel):
    id: str
    name: str
    category: str
    color: str
    icon: str
    options: list[ExtensionOption]


class ModelDefinition(BaseModel):
    id: str
    name: str
    family: str
    version: str
    description: str
    sizes: Optional[dict] = None
    layers: list[LayerDefinition]
    head: dict
    extensions: list[Extension]


def _load_model_json(filename: str) -> dict:
    """Load a model JSON file from the models directory."""
    filepath = MODELS_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Model file not found: {filename}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _scan_models() -> list[dict]:
    """Scan the models directory and return metadata for all available models."""
    models = []
    if not MODELS_DIR.exists():
        return models
    for f in sorted(MODELS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            models.append({
                "id": data.get("id", f.stem),
                "name": data.get("name", f.stem),
                "family": data.get("family", "unknown"),
                "version": data.get("version", "1"),
                "description": data.get("description", ""),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return models


@router.get("/models")
@limiter.limit("60/minute")
async def list_models(request: Request):
    """
    List all available model families and their versions.

    Returns a list of model metadata (id, name, family, version, description).
    """
    all_models = _scan_models()

    # Group by family
    families: dict[str, list[dict]] = {}
    for m in all_models:
        fam = m["family"]
        if fam not in families:
            families[fam] = []
        families[fam].append(m)

    result = []
    for family_name, models_in_family in families.items():
        result.append({
            "family": family_name,
            "name": family_name,
            "description": models_in_family[0].get("description", ""),
            "versions": [m["version"] for m in models_in_family],
        })

    return {"families": result, "total_models": len(all_models)}


@router.get("/models/{family}/{version}")
@limiter.limit("60/minute")
async def get_model_definition(request: Request, family: str, version: str):
    """
    Get the full model definition for a specific family and version.

    Returns layers, extensions, options, descriptions, code snippets, etc.
    """
    # Find matching model file
    all_models = _scan_models()
    match = None
    for m in all_models:
        if m["family"].lower() == family.lower() and m["version"] == version:
            match = m
            break

    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {family} v{version}. Use GET /api/models to list available models.",
        )

    # Load full definition
    filename = f"{match['id']}.json"
    data = _load_model_json(filename)
    return data
