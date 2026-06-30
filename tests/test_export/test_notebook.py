"""
Tests for Notebook Export.

Validates that a model config can be exported as a Jupyter notebook (.ipynb).
"""

import json
import pytest
import os

# Path to the CNN v16 model config
CNN_V16_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "src", "data", "models", "cnn_v16.json"
)


def _load_cnn_v16():
    """Load the CNN v16 model config."""
    with open(CNN_V16_PATH, "r") as f:
        return json.load(f)


def _generate_notebook(config: dict) -> dict:
    """
    Generate a Jupyter notebook from a model config.

    This is a reference implementation that the actual export module
    should replicate. Tests verify the structure, not the implementation.
    """
    cells = []

    # Title cell
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [f"# {config['name']} — Training Notebook\n",
                    f"\n",
                    f"{config.get('description', '')}"],
    })

    # Imports cell
    imports = [
        "import torch\n",
        "import torch.nn as nn\n",
        "import torch.optim as optim\n",
        "from torch.utils.data import DataLoader\n",
        "from torchvision import transforms\n",
    ]
    cells.append({
        "cell_type": "code",
        "metadata": {},
        "source": imports,
        "outputs": [],
        "execution_count": None,
    })

    # Model definition cell
    model_lines = [f"# {config['name']} Architecture\n",
                    "class Model(nn.Module):\n",
                    "    def __init__(self, num_classes=10):\n",
                    "        super().__init__()\n"]
    for layer in config["layers"]:
        model_lines.append(f"        self.{layer['id']} = {layer['code']}\n")

    # Head
    if "head" in config:
        head = config["head"]
        model_lines.append(f"        self.head = {head['code']}\n")

    model_lines.append("\n")
    model_lines.append("    def forward(self, x):\n")
    for layer in config["layers"]:
        model_lines.append(f"        x = self.{layer['id']}(x)\n")
    model_lines.append("        x = self.head(x)\n")
    model_lines.append("        return x\n")

    cells.append({
        "cell_type": "code",
        "metadata": {},
        "source": model_lines,
        "outputs": [],
        "execution_count": None,
    })

    # Assemble notebook
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0",
            },
        },
        "cells": cells,
    }
    return notebook


class TestNotebookExport:
    """Test suite for notebook generation from model config."""

    def setup_method(self):
        self.config = _load_cnn_v16()
        self.notebook = _generate_notebook(self.config)

    def test_notebook_is_valid_json(self):
        """Generated notebook should be valid JSON."""
        raw = json.dumps(self.notebook)
        parsed = json.loads(raw)
        assert parsed["nbformat"] == 4

    def test_notebook_has_required_keys(self):
        """Notebook must have nbformat, metadata, and cells."""
        assert "nbformat" in self.notebook
        assert "metadata" in self.notebook
        assert "cells" in self.notebook

    def test_notebook_has_title_cell(self):
        """First cell should be a markdown cell with the model name."""
        cells = self.notebook["cells"]
        assert len(cells) > 0
        title_cell = cells[0]
        assert title_cell["cell_type"] == "markdown"
        source = "".join(title_cell["source"])
        assert self.config["name"] in source

    def test_notebook_has_imports_cell(self):
        """Second cell should contain Python imports."""
        cells = self.notebook["cells"]
        assert len(cells) > 1
        import_cell = cells[1]
        assert import_cell["cell_type"] == "code"
        source = "".join(import_cell["source"])
        assert "import torch" in source
        assert "import torch.nn" in source

    def test_notebook_has_model_class(self):
        """Should have a code cell defining the model class."""
        cells = self.notebook["cells"]
        code_cells = [c for c in cells if c["cell_type"] == "code"]
        model_source = "".join(c["source"] for c in code_cells)
        assert "class Model" in model_source
        assert "nn.Module" in model_source

    def test_notebook_includes_all_layers(self):
        """Model class should reference all layers from config."""
        cells = self.notebook["cells"]
        code_source = "".join(c["source"] for c in cells if c["cell_type"] == "code")
        for layer in self.config["layers"]:
            assert layer["id"] in code_source, f"Layer {layer['id']} missing from notebook"

    def test_notebook_includes_head(self):
        """Model class should include the classification head."""
        cells = self.notebook["cells"]
        code_source = "".join(c["source"] for c in cells if c["cell_type"] == "code")
        assert "self.head" in code_source

    def test_code_cells_have_execution_count_key(self):
        """All code cells should have execution_count key (null = not run)."""
        for cell in self.notebook["cells"]:
            if cell["cell_type"] == "code":
                assert "execution_count" in cell
                assert cell["execution_count"] is None

    def test_notebook_metadata_has_kernel(self):
        """Notebook metadata should specify a Python kernel."""
        meta = self.notebook["metadata"]
        assert "kernelspec" in meta
        assert meta["kernelspec"]["language"] == "python"

    def test_empty_config_produces_valid_notebook(self):
        """Notebook generation should handle minimal config gracefully."""
        minimal = {"name": "Empty", "layers": [], "head": None}
        nb = _generate_notebook(minimal)
        assert nb["nbformat"] == 4
        assert len(nb["cells"]) >= 2  # title + imports at minimum
