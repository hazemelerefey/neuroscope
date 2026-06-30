"""
Export API Route — Generate Jupyter notebooks and YAML from visual builder configurations.
"""

import io
import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class LayerConfig(BaseModel):
    """A single layer in the user's visual model configuration."""
    id: str
    type: str
    name: str
    params: dict = {}


class ExtensionChoice(BaseModel):
    """User's choice for an extension (optimizer, loss, etc.)."""
    extension_id: str
    option_id: str


class ExportNotebookRequest(BaseModel):
    """Request to generate a Jupyter notebook from a visual configuration."""
    model_family: str
    model_version: str
    model_name: str = "MyModel"
    layers: list[LayerConfig]
    extensions: list[ExtensionChoice]
    num_classes: int = 10
    input_shape: list[int] = [3, 224, 224]


class ExportYamlRequest(BaseModel):
    """Request to generate a YAML model configuration."""
    model_family: str
    model_version: str
    model_name: str = "MyModel"
    layers: list[LayerConfig]
    extensions: list[ExtensionChoice]
    num_classes: int = 10
    input_shape: list[int] = [3, 224, 224]


def _build_imports_code() -> str:
    """Generate the import statements for a notebook."""
    return (
        "import torch\n"
        "import torch.nn as nn\n"
        "import torch.optim as optim\n"
        "import torchvision\n"
        "import torchvision.transforms as transforms\n"
        "from torch.utils.data import DataLoader\n"
    )


def _build_model_class_code(layers: list[LayerConfig], head_code: str, num_classes: int) -> str:
    """Generate the PyTorch model class code."""
    lines = [
        "",
        "",
        "class CustomModel(nn.Module):",
        "    def __init__(self, num_classes):",
        "        super().__init__()",
        "",
    ]

    for layer in layers:
        code = layer.params.get("code", f"# {layer.name}")
        lines.append(f"        self.{layer.id} = {code}")

    lines.append("")
    lines.append(f"        self.head = nn.LazyLinear(num_classes)")
    lines.append("")
    lines.append("    def forward(self, x):")

    # Build forward pass
    for i, layer in enumerate(layers):
        if i == 0:
            lines.append(f"        x = self.{layer.id}(x)")
        else:
            lines.append(f"        x = self.{layer.id}(x)")

    lines.append(f"        x = self.head(x)")
    lines.append("        return x")
    lines.append("")
    lines.append(f"model = CustomModel(num_classes={num_classes})")
    lines.append("print(model)")
    return "\n".join(lines)


def _build_extension_code(extensions: list[ExtensionChoice], model_data: dict) -> str:
    """Generate code for chosen extensions (optimizer, loss, etc.)."""
    lines = [""]

    # Build a lookup from the model definition
    ext_lookup: dict[str, dict] = {}
    for ext in model_data.get("extensions", []):
        for opt in ext.get("options", []):
            ext_lookup[f"{ext['id']}:{opt['id']}"] = {
                "code": opt.get("code", ""),
                "name": opt.get("name", ""),
                "ext_name": ext.get("name", ""),
            }

    for choice in extensions:
        key = f"{choice.extension_id}:{choice.option_id}"
        entry = ext_lookup.get(key)
        if entry:
            lines.append(f"# {entry['ext_name']}: {entry['name']}")
            lines.append(entry["code"])
        else:
            lines.append(f"# Unknown extension choice: {key}")

    return "\n".join(lines)


def _build_training_loop_code() -> str:
    """Generate a basic training loop."""
    return """
# Training loop
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    train_acc = 100.0 * correct / total
    avg_loss = running_loss / len(train_loader)
    print(f"Epoch [{epoch+1}/{num_epochs}] Loss: {avg_loss:.4f} Acc: {train_acc:.2f}%")
"""


@router.post("/export/notebook")
@limiter.limit("20/minute")
async def export_notebook(request: Request, body: ExportNotebookRequest):
    """
    Generate a Jupyter notebook from a visual builder configuration.

    The notebook includes:
    - Imports
    - Model class definition
    - Extension code (optimizer, loss, etc.)
    - Training loop
    """
    try:
        import nbformat as nbf
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="nbformat is required for notebook generation. Install with: pip install nbformat",
        )

    # Load model definition to get extension code snippets
    model_data = _load_model_definition(body.model_family, body.model_version)

    nb = nbf.v4.new_notebook()
    cells = []

    # Title cell
    cells.append(nbf.v4.new_markdown_cell(
        f"# {body.model_name}\n"
        f"Generated by NeuroScope Visual Deep Learning Builder\n\n"
        f"**Architecture:** {body.model_family} v{body.model_version}  \n"
        f"**Layers:** {len(body.layers)}  \n"
        f"**Classes:** {body.num_classes}  \n"
        f"**Input shape:** {body.input_shape}"
    ))

    # Imports
    cells.append(nbf.v4.new_code_cell(_build_imports_code()))

    # Model definition
    head_code = model_data.get("head", {}).get("code", "nn.LazyLinear(num_classes)")
    cells.append(nbf.v4.new_code_cell(
        _build_model_class_code(body.layers, head_code, body.num_classes)
    ))

    # Extensions (optimizer, loss, etc.)
    ext_code = _build_extension_code(body.extensions, model_data)
    if ext_code.strip():
        cells.append(nbf.v4.new_markdown_cell("## Training Configuration"))
        cells.append(nbf.v4.new_code_cell(ext_code))

    # Training loop
    cells.append(nbf.v4.new_markdown_cell("## Training"))
    cells.append(nbf.v4.new_code_cell(_build_training_loop_code()))

    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0",
        },
    }

    content = nbf.writes(nb)
    filename = f"{body.model_name.replace(' ', '_')}.ipynb"

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/x-ipynb+json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/yaml")
@limiter.limit("20/minute")
async def export_yaml(request: Request, body: ExportYamlRequest):
    """
    Generate a YAML model configuration from a visual builder setup.

    Produces a structured YAML file describing the model architecture,
    layer configurations, and training hyperparameters.
    """
    try:
        import yaml
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="pyyaml is required for YAML export. Install with: pip install pyyaml",
        )

    model_data = _load_model_definition(body.model_family, body.model_version)

    # Build extension lookup
    ext_lookup: dict[str, dict] = {}
    for ext in model_data.get("extensions", []):
        for opt in ext.get("options", []):
            ext_lookup[f"{ext['id']}:{opt['id']}"] = {
                "code": opt.get("code", ""),
                "name": opt.get("name", ""),
                "ext_name": ext.get("name", ""),
            }

    # Build YAML structure
    config = {
        "model": {
            "name": body.model_name,
            "family": body.model_family,
            "version": body.model_version,
            "num_classes": body.num_classes,
            "input_shape": body.input_shape,
        },
        "layers": [
            {
                "id": layer.id,
                "type": layer.type,
                "name": layer.name,
                "params": {k: v for k, v in layer.params.items() if k != "code"},
            }
            for layer in body.layers
        ],
        "training": {},
    }

    # Add extension choices
    for choice in body.extensions:
        key = f"{choice.extension_id}:{choice.option_id}"
        entry = ext_lookup.get(key)
        if entry:
            config["training"][entry["ext_name"].lower().replace(" ", "_")] = {
                "choice": entry["name"],
                "code": entry["code"],
            }

    content = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
    filename = f"{body.model_name.replace(' ', '_')}_config.yaml"

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/x-yaml",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _load_model_definition(family: str, version: str) -> dict:
    """Load a model definition JSON by family and version."""
    from pathlib import Path

    models_dir = Path(__file__).resolve().parent.parent.parent / "data" / "models"
    if not models_dir.exists():
        raise HTTPException(status_code=500, detail="Models directory not found")

    for f in models_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("family", "").lower() == family.lower() and data.get("version") == version:
                return data
        except (json.JSONDecodeError, KeyError):
            continue

    raise HTTPException(
        status_code=404,
        detail=f"Model definition not found: {family} v{version}",
    )
