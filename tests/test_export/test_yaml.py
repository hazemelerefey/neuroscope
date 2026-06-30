"""
Tests for YAML Export.

Validates that a model config can be exported as a YAML training configuration.
"""

import json
import os

import pytest
import yaml

# Path to the CNN v16 model config
CNN_V16_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "src", "data", "models", "cnn_v16.json"
)


def _load_cnn_v16():
    """Load the CNN v16 model config."""
    with open(CNN_V16_PATH, "r") as f:
        return json.load(f)


def _generate_yaml_config(config: dict, selections: dict = None) -> dict:
    """
    Generate a YAML training configuration from a model config and user selections.

    This is a reference implementation. The actual export module should replicate this.
    """
    if selections is None:
        selections = {}

    # Collect defaults from extensions
    extensions = config.get("extensions", [])
    defaults = {}
    for ext in extensions:
        for opt in ext.get("options", []):
            if opt.get("default"):
                defaults[ext["id"]] = opt["id"]

    # Merge defaults with user selections
    resolved = {**defaults, **selections}

    yaml_config = {
        "model": {
            "name": config["name"],
            "family": config["family"],
            "version": config["version"],
        },
        "architecture": {
            "layers": [
                {
                    "id": layer["id"],
                    "type": layer["type"],
                    "params": layer["params"],
                }
                for layer in config["layers"]
            ],
            "head": {
                "type": config["head"]["type"],
                "output_neurons": config["head"]["output_neurons"],
                "activation": config["head"]["activation"],
            },
        },
        "training": {},
    }

    # Map resolved selections to training config
    for ext in extensions:
        ext_id = ext["id"]
        selected_id = resolved.get(ext_id)
        if selected_id:
            selected_opt = next(
                (o for o in ext["options"] if o["id"] == selected_id), None
            )
            if selected_opt:
                yaml_config["training"][ext_id] = {
                    "id": selected_opt["id"],
                    "name": selected_opt["name"],
                }

    return yaml_config


class TestYamlExport:
    """Test suite for YAML export from model config."""

    def setup_method(self):
        self.config = _load_cnn_v16()
        self.yaml_config = _generate_yaml_config(self.config)

    def test_yaml_is_valid(self):
        """Generated YAML config should serialize and parse cleanly."""
        raw = yaml.dump(self.yaml_config)
        parsed = yaml.safe_load(raw)
        assert parsed["model"]["name"] == self.config["name"]

    def test_yaml_has_model_section(self):
        """YAML config should have a model section with name/family/version."""
        model = self.yaml_config["model"]
        assert model["name"] == "CNN v16"
        assert model["family"] == "CNN"
        assert model["version"] == "16"

    def test_yaml_has_architecture_section(self):
        """YAML config should have architecture with layers and head."""
        arch = self.yaml_config["architecture"]
        assert "layers" in arch
        assert "head" in arch
        assert len(arch["layers"]) == len(self.config["layers"])

    def test_yaml_layer_ids_match_config(self):
        """Layer IDs in YAML should match the model config."""
        yaml_layer_ids = [l["id"] for l in self.yaml_config["architecture"]["layers"]]
        config_layer_ids = [l["id"] for l in self.config["layers"]]
        assert yaml_layer_ids == config_layer_ids

    def test_yaml_training_has_defaults(self):
        """Training section should use default selections from extensions."""
        training = self.yaml_config["training"]
        # CNN v16 should have defaults for optimizer, loss, lr, etc.
        assert "optimizer" in training
        assert "loss" in training
        assert "learning_rate" in training

    def test_yaml_default_optimizer_is_adamw(self):
        """Default optimizer should be AdamW (per cnn_v16.json defaults)."""
        assert self.yaml_config["training"]["optimizer"]["id"] == "adamw"

    def test_yaml_default_loss_is_cross_entropy(self):
        """Default loss should be Cross-Entropy Loss."""
        assert self.yaml_config["training"]["loss"]["id"] == "cross_entropy"

    def test_yaml_with_custom_selections(self):
        """User selections should override defaults."""
        custom = _generate_yaml_config(
            self.config,
            selections={"optimizer": "sgd", "batch_size": "batch_64"},
        )
        assert custom["training"]["optimizer"]["id"] == "sgd"
        assert custom["training"]["batch_size"]["id"] == "batch_64"

    def test_yaml_serialization_roundtrip(self):
        """Config should survive YAML serialize → deserialize roundtrip."""
        raw = yaml.dump(self.yaml_config)
        restored = yaml.safe_load(raw)
        assert restored == self.yaml_config

    def test_yaml_head_has_activation(self):
        """Head section should specify the activation function."""
        head = self.yaml_config["architecture"]["head"]
        assert head["activation"] == "softmax"

    def test_empty_config_produces_valid_yaml(self):
        """YAML generation should handle minimal config gracefully."""
        minimal = {"name": "Empty", "family": "test", "version": "1", "layers": [], "head": {"type": "linear", "output_neurons": "num_classes", "activation": "softmax"}, "extensions": []}
        cfg = _generate_yaml_config(minimal)
        raw = yaml.dump(cfg)
        parsed = yaml.safe_load(raw)
        assert parsed["model"]["name"] == "Empty"
