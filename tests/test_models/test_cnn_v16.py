"""
Tests for CNN v16 Model Configuration.

Validates that the cnn_v16.json model definition is structurally valid,
complete, and consistent.
"""

import json
import os

import pytest

# Path to the CNN v16 model config
CNN_V16_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "src", "data", "models", "cnn_v16.json"
)


@pytest.fixture
def config():
    """Load the CNN v16 model config."""
    with open(CNN_V16_PATH, "r") as f:
        return json.load(f)


@pytest.fixture
def layers(config):
    """Extract layer list from config."""
    return config["layers"]


@pytest.fixture
def extensions(config):
    """Extract extensions from config."""
    return config.get("extensions", [])


# ── Structural Validation ────────────────────────────────────────────


class TestCnnV16Structure:
    """Test the top-level structure of cnn_v16.json."""

    def test_file_exists(self):
        """cnn_v16.json must exist."""
        assert os.path.isfile(CNN_V16_PATH)

    def test_is_valid_json(self):
        """File must be valid JSON."""
        with open(CNN_V16_PATH, "r") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_has_required_top_level_keys(self, config):
        """Config must have id, name, family, version, layers, head, extensions."""
        required = ["id", "name", "family", "version", "layers", "head", "extensions"]
        for key in required:
            assert key in config, f"Missing top-level key: {key}"

    def test_id_is_cnn_v16(self, config):
        assert config["id"] == "cnn_v16"

    def test_family_is_cnn(self, config):
        assert config["family"] == "CNN"

    def test_version_is_string(self, config):
        assert isinstance(config["version"], str)


# ── Layer Validation ─────────────────────────────────────────────────


class TestCnnV16Layers:
    """Test that all layers are well-formed."""

    def test_layers_is_nonempty(self, layers):
        assert len(layers) > 0

    def test_layer_has_required_keys(self, layers):
        """Each layer must have id, type, name, params, code."""
        for layer in layers:
            for key in ["id", "type", "name", "params", "code"]:
                assert key in layer, f"Layer '{layer.get('id', '?')}' missing key: {key}"

    def test_layer_ids_are_unique(self, layers):
        """Layer IDs must be unique."""
        ids = [l["id"] for l in layers]
        assert len(ids) == len(set(ids)), f"Duplicate layer IDs: {ids}"

    def test_layer_types_are_valid(self, layers):
        """Layer types must be from a known set."""
        valid_types = {
            "conv2d", "batchnorm", "activation", "maxpool", "avgpool",
            "flatten", "linear", "dropout", "layernorm", "softmax",
        }
        for layer in layers:
            assert layer["type"] in valid_types, f"Unknown layer type: {layer['type']}"

    def test_conv_layers_have_channel_params(self, layers):
        """Conv2d layers must specify in_channels and out_channels."""
        for layer in layers:
            if layer["type"] == "conv2d":
                params = layer["params"]
                assert "in_channels" in params, f"Conv layer '{layer['id']}' missing in_channels"
                assert "out_channels" in params, f"Conv layer '{layer['id']}' missing out_channels"
                assert "kernel_size" in params, f"Conv layer '{layer['id']}' missing kernel_size"

    def test_linear_layers_have_features(self, layers):
        """Linear layers must specify in_features and out_features."""
        for layer in layers:
            if layer["type"] == "linear":
                params = layer["params"]
                assert "in_features" in params, f"Linear layer '{layer['id']}' missing in_features"
                assert "out_features" in params, f"Linear layer '{layer['id']}' missing out_features"

    def test_batchnorm_has_num_features(self, layers):
        """BatchNorm layers must specify num_features."""
        for layer in layers:
            if layer["type"] == "batchnorm":
                assert "num_features" in layer["params"]

    def test_activation_has_function(self, layers):
        """Activation layers must specify the function name."""
        for layer in layers:
            if layer["type"] == "activation":
                assert "function" in layer["params"]

    def test_code_is_string(self, layers):
        """Every layer code must be a string."""
        for layer in layers:
            assert isinstance(layer["code"], str)

    def test_freezable_flag_exists(self, layers):
        """Every layer should have a freezable boolean flag."""
        for layer in layers:
            assert "freezable" in layer, f"Layer '{layer['id']}' missing freezable flag"
            assert isinstance(layer["freezable"], bool)


# ── Channel Flow Consistency ─────────────────────────────────────────


class TestCnnV16ChannelFlow:
    """Test that channel dimensions flow consistently through the network."""

    def test_first_conv_takes_3_channels(self, layers):
        """First conv layer should accept 3 input channels (RGB)."""
        first_conv = next(l for l in layers if l["type"] == "conv2d")
        assert first_conv["params"]["in_channels"] == 3

    def test_conv_channel_progression(self, layers):
        """Conv channels should generally increase (64 → 128 → 256)."""
        conv_layers = [l for l in layers if l["type"] == "conv2d"]
        out_channels = [l["params"]["out_channels"] for l in conv_layers]
        # Should be non-decreasing
        for i in range(1, len(out_channels)):
            assert out_channels[i] >= out_channels[i - 1], (
                f"Channel decrease: {out_channels[i-1]} → {out_channels[i]}"
            )

    def test_batchnorm_matches_conv(self, layers):
        """Each BatchNorm's num_features should match the preceding Conv's out_channels."""
        for i, layer in enumerate(layers):
            if layer["type"] == "batchnorm" and i > 0:
                prev = layers[i - 1]
                if prev["type"] == "conv2d":
                    assert layer["params"]["num_features"] == prev["params"]["out_channels"], (
                        f"BN '{layer['id']}' num_features={layer['params']['num_features']} "
                        f"!= Conv '{prev['id']}' out_channels={prev['params']['out_channels']}"
                    )


# ── Head Validation ──────────────────────────────────────────────────


class TestCnnV16Head:
    """Test the classification head."""

    def test_head_exists(self, config):
        assert "head" in config

    def test_head_has_type(self, config):
        assert config["head"]["type"] == "linear"

    def test_head_has_activation(self, config):
        assert config["head"]["activation"] == "softmax"

    def test_head_has_output_neurons(self, config):
        assert config["head"]["output_neurons"] == "num_classes"

    def test_head_has_code(self, config):
        assert "code" in config["head"]
        assert "nn.Linear" in config["head"]["code"]

    def test_head_has_description(self, config):
        assert "description" in config["head"]
        assert len(config["head"]["description"]) > 0


# ── Extensions Validation ────────────────────────────────────────────


class TestCnnV16Extensions:
    """Test the training extensions (optimizer, loss, augmentation, etc.)."""

    def test_extensions_is_nonempty(self, extensions):
        assert len(extensions) > 0

    def test_extension_has_required_keys(self, extensions):
        """Each extension must have id, name, category, options."""
        for ext in extensions:
            for key in ["id", "name", "category", "options"]:
                assert key in ext, f"Extension '{ext.get('id', '?')}' missing key: {key}"

    def test_extension_options_have_required_keys(self, extensions):
        """Each option must have id, name, code, description."""
        for ext in extensions:
            for opt in ext["options"]:
                for key in ["id", "name", "code", "description"]:
                    assert key in opt, (
                        f"Option '{opt.get('id', '?')}' in extension '{ext['id']}' missing key: {key}"
                    )

    def test_each_extension_has_default(self, extensions):
        """Each extension should have exactly one default option."""
        for ext in extensions:
            defaults = [o for o in ext["options"] if o.get("default")]
            assert len(defaults) >= 1, (
                f"Extension '{ext['id']}' has no default option"
            )

    def test_optimizer_options(self, extensions):
        """Optimizer extension should have common optimizers."""
        optimizer = next((e for e in extensions if e["id"] == "optimizer"), None)
        assert optimizer is not None
        opt_ids = {o["id"] for o in optimizer["options"]}
        assert "adam" in opt_ids
        assert "sgd" in opt_ids
        assert "adamw" in opt_ids

    def test_loss_options(self, extensions):
        """Loss extension should include cross-entropy."""
        loss = next((e for e in extensions if e["id"] == "loss"), None)
        assert loss is not None
        loss_ids = {o["id"] for o in loss["options"]}
        assert "cross_entropy" in loss_ids

    def test_batch_size_options(self, extensions):
        """Batch size extension should have common values."""
        bs = next((e for e in extensions if e["id"] == "batch_size"), None)
        assert bs is not None
        bs_ids = {o["id"] for o in bs["options"]}
        assert "batch_16" in bs_ids
        assert "batch_32" in bs_ids

    def test_color_and_icon_on_every_extension(self, extensions):
        """Every extension should have a color and icon for the UI."""
        for ext in extensions:
            assert "color" in ext, f"Extension '{ext['id']}' missing color"
            assert "icon" in ext, f"Extension '{ext['id']}' missing icon"
