"""
Keras/TensorFlow Model Parser — Parses .h5 and .keras files.

Extracts layers and their configuration from Keras models,
then converts to NeuroScopeGraph.
"""

import os
from typing import Optional

from src.graph import Edge, LayerNode, NeuroScopeGraph
from src.parsers import BaseParser

# Keras layer class name → NeuroScope category
_LAYER_CATEGORIES = {
    "Conv1D": "convolution",
    "Conv2D": "convolution",
    "Conv3D": "convolution",
    "SeparableConv1D": "convolution",
    "SeparableConv2D": "convolution",
    "DepthwiseConv2D": "convolution",
    "Conv1DTranspose": "convolution",
    "Conv2DTranspose": "convolution",
    "Conv3DTranspose": "convolution",
    "Dense": "linear",
    "MaxPooling1D": "pooling",
    "MaxPooling2D": "pooling",
    "MaxPooling3D": "pooling",
    "AveragePooling1D": "pooling",
    "AveragePooling2D": "pooling",
    "AveragePooling3D": "pooling",
    "GlobalMaxPooling1D": "pooling",
    "GlobalMaxPooling2D": "pooling",
    "GlobalAveragePooling1D": "pooling",
    "GlobalAveragePooling2D": "pooling",
    "BatchNormalization": "normalization",
    "LayerNormalization": "normalization",
    "GroupNormalization": "normalization",
    "UnitNormalization": "normalization",
    "Activation": "activation",
    "ReLU": "activation",
    "LeakyReLU": "activation",
    "PReLU": "activation",
    "ELU": "activation",
    "ThresholdedReLU": "activation",
    "Softmax": "activation",
    "Dropout": "regularization",
    "SpatialDropout1D": "regularization",
    "SpatialDropout2D": "regularization",
    "SpatialDropout3D": "regularization",
    "GaussianDropout": "regularization",
    "AlphaDropout": "regularization",
    "Flatten": "reshape",
    "Reshape": "reshape",
    "Permute": "reshape",
    "RepeatVector": "reshape",
    "ZeroPadding1D": "utility",
    "ZeroPadding2D": "utility",
    "ZeroPadding3D": "utility",
    "Cropping1D": "utility",
    "Cropping2D": "utility",
    "Cropping3D": "utility",
    "UpSampling1D": "utility",
    "UpSampling2D": "utility",
    "UpSampling3D": "utility",
    "LSTM": "recurrent",
    "GRU": "recurrent",
    "SimpleRNN": "recurrent",
    "Bidirectional": "recurrent",
    "Embedding": "embedding",
    "MultiHeadAttention": "attention",
    "Attention": "attention",
    "Add": "combination",
    "Concatenate": "combination",
    "Multiply": "combination",
    "Subtract": "combination",
    "InputLayer": "input",
    "Input": "input",
}

# Keras layer class name → NeuroScope op_type
_LAYER_TO_OP = {
    "Conv1D": "Conv",
    "Conv2D": "Conv",
    "Conv3D": "Conv",
    "SeparableConv1D": "Conv",
    "SeparableConv2D": "Conv",
    "DepthwiseConv2D": "Conv",
    "Conv1DTranspose": "ConvTranspose",
    "Conv2DTranspose": "ConvTranspose",
    "Conv3DTranspose": "ConvTranspose",
    "Dense": "Gemm",
    "MaxPooling1D": "MaxPool",
    "MaxPooling2D": "MaxPool",
    "MaxPooling3D": "MaxPool",
    "AveragePooling1D": "AveragePool",
    "AveragePooling2D": "AveragePool",
    "AveragePooling3D": "AveragePool",
    "GlobalMaxPooling1D": "GlobalMaxPool",
    "GlobalMaxPooling2D": "GlobalMaxPool",
    "GlobalAveragePooling1D": "GlobalAveragePool",
    "GlobalAveragePooling2D": "GlobalAveragePool",
    "BatchNormalization": "BatchNormalization",
    "LayerNormalization": "LayerNormalization",
    "GroupNormalization": "GroupNormalization",
    "UnitNormalization": "LayerNormalization",
    "Activation": "Relu",
    "ReLU": "Relu",
    "LeakyReLU": "LeakyRelu",
    "PReLU": "PRelu",
    "ELU": "Elu",
    "ThresholdedReLU": "Relu",
    "Softmax": "Softmax",
    "Dropout": "Dropout",
    "SpatialDropout1D": "Dropout",
    "SpatialDropout2D": "Dropout",
    "SpatialDropout3D": "Dropout",
    "GaussianDropout": "Dropout",
    "AlphaDropout": "Dropout",
    "Flatten": "Flatten",
    "Reshape": "Reshape",
    "Permute": "Transpose",
    "RepeatVector": "Reshape",
    "LSTM": "LSTM",
    "GRU": "GRU",
    "SimpleRNN": "RNN",
    "Bidirectional": "LSTM",
    "Embedding": "Embedding",
    "MultiHeadAttention": "MultiHeadAttention",
    "Attention": "Attention",
    "Add": "Add",
    "Concatenate": "Concat",
    "Multiply": "Mul",
    "Subtract": "Add",
    "InputLayer": "Input",
    "Input": "Input",
}

_DESCRIPTIONS = {
    "Conv": "Applies convolutional filters to extract spatial features.",
    "Gemm": "Dense/fully-connected layer. Each output is a weighted sum of all inputs.",
    "Relu": "Rectified Linear Unit — outputs max(0, x).",
    "BatchNormalization": "Normalizes activations across the batch.",
    "MaxPool": "Reduces spatial dimensions by taking the maximum in each window.",
    "AveragePool": "Reduces spatial dimensions by averaging values.",
    "GlobalAveragePool": "Averages each feature map to a single value.",
    "Dropout": "Randomly zeros neurons during training. Prevents overfitting.",
    "Flatten": "Reshapes multi-dimensional tensor to 1D.",
    "LSTM": "Long Short-Term Memory — captures long-range dependencies.",
    "GRU": "Gated Recurrent Unit — simplified alternative to LSTM.",
    "Softmax": "Converts logits to probabilities for classification.",
    "Embedding": "Maps integer indices to dense vectors.",
}


class KerasParser(BaseParser):
    """Parser for Keras/TensorFlow model files (.h5, .keras)."""

    def supports(self, file_path: str) -> bool:
        """Check if file has a Keras extension."""
        return file_path.lower().endswith((".h5", ".keras"))

    def parse(self, file_path: str, **kwargs) -> NeuroScopeGraph:
        """
        Parse a Keras model file into a NeuroScopeGraph.

        Supports:
        - HDF5 format (.h5)
        - Keras native format (.keras)
        - SavedModel directories (if they contain .pb files)

        Args:
            file_path: Path to the model file.
            **kwargs: Optional arguments (currently unused).

        Returns:
            NeuroScopeGraph representation.

        Raises:
            ImportError: If tensorflow is not installed.
            FileNotFoundError: If file doesn't exist.
            ValueError: If file cannot be parsed.
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise ImportError(
                "tensorflow package not installed. Run: pip install tensorflow"
            )

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")

        # Load model
        try:
            model = tf.keras.models.load_model(file_path, compile=False)
        except Exception as e:
            raise ValueError(f"Failed to load Keras model: {e}")

        return self._parse_keras_model(model, file_path)

    def _parse_keras_model(self, model: "tf.keras.Model", file_path: str) -> NeuroScopeGraph:
        """
        Parse a loaded Keras model into a NeuroScopeGraph.

        Args:
            model: Loaded Keras model.
            file_path: Original file path for metadata.

        Returns:
            NeuroScopeGraph.
        """
        nodes = []
        edges = []

        # Track layer name → node id for edge building
        layer_name_to_id: dict[str, int] = {}

        try:
            layers = model.layers
        except Exception:
            layers = []

        for idx, layer in enumerate(layers):
            class_name = type(layer).__name__
            op_type = _LAYER_TO_OP.get(class_name, class_name)
            category = _LAYER_CATEGORIES.get(class_name, "other")
            description = _DESCRIPTIONS.get(op_type, "")

            # Extract attributes from config
            attributes = self._extract_config(layer)

            # Count parameters
            try:
                params = layer.count_params()
            except Exception:
                params = 0

            # Get input/output shapes
            input_shapes = self._get_input_shapes(layer)
            output_shapes = self._get_output_shapes(layer)

            node = LayerNode(
                id=idx,
                name=layer.name or f"{class_name}_{idx}",
                op_type=op_type,
                category=category,
                input_shapes=input_shapes,
                output_shapes=output_shapes,
                attributes=attributes,
                params=params,
                description=description,
            )
            nodes.append(node)
            layer_name_to_id[layer.name] = idx

        # Build edges from layer inbound connections
        edges = self._build_edges(model, layer_name_to_id)

        # If no edges found, build sequential edges
        if not edges and len(nodes) > 1:
            for i in range(len(nodes) - 1):
                edges.append(Edge(source_id=i, target_id=i + 1))

        graph = NeuroScopeGraph(
            nodes=nodes,
            edges=edges,
            model_name=os.path.basename(file_path),
            framework="keras",
        )
        graph.compute_aggregates()
        return graph

    def _extract_config(self, layer: "tf.keras.layers.Layer") -> dict:
        """Extract configuration attributes from a Keras layer."""
        attrs = {}

        try:
            config = layer.get_config()
        except Exception:
            return attrs

        # Convolution
        if "kernel_size" in config:
            ks = config["kernel_size"]
            attrs["kernel_shape"] = list(ks) if isinstance(ks, (tuple, list)) else [ks]
        if "strides" in config:
            s = config["strides"]
            attrs["strides"] = list(s) if isinstance(s, (tuple, list)) else [s]
        if "padding" in config:
            attrs["padding"] = config["padding"]
        if "dilation_rate" in config:
            d = config["dilation_rate"]
            attrs["dilations"] = list(d) if isinstance(d, (tuple, list)) else [d]
        if "groups" in config:
            attrs["group"] = config["groups"]

        # Dense
        if "units" in config:
            attrs["out_features"] = config["units"]

        # Normalization
        if "epsilon" in config:
            attrs["epsilon"] = config["epsilon"]
        if "momentum" in config:
            attrs["momentum"] = config["momentum"]

        # Dropout
        if "rate" in config:
            attrs["ratio"] = config["rate"]

        # RNN
        if "return_sequences" in config:
            attrs["return_sequences"] = config["return_sequences"]
        if "return_state" in config:
            attrs["return_state"] = config["return_state"]

        # Embedding
        if "input_dim" in config:
            attrs["vocab_size"] = config["input_dim"]
        if "output_dim" in config:
            attrs["embedding_dim"] = config["output_dim"]

        # Attention
        if "num_heads" in config:
            attrs["num_heads"] = config["num_heads"]
        if "key_dim" in config:
            attrs["key_dim"] = config["key_dim"]

        return attrs

    def _get_input_shapes(self, layer: "tf.keras.layers.Layer") -> list[list[int]]:
        """Get input shapes from a Keras layer."""
        shapes = []
        try:
            if hasattr(layer, "input_shape") and layer.input_shape:
                shape = layer.input_shape
                if isinstance(shape, (tuple, list)):
                    if shape and isinstance(shape[0], (tuple, list)):
                        # Multiple inputs
                        for s in shape:
                            shapes.append(list(s) if s else [])
                    else:
                        shapes.append(list(shape))
        except Exception:
            pass
        return shapes

    def _get_output_shapes(self, layer: "tf.keras.layers.Layer") -> list[list[int]]:
        """Get output shapes from a Keras layer."""
        shapes = []
        try:
            if hasattr(layer, "output_shape") and layer.output_shape:
                shape = layer.output_shape
                if isinstance(shape, (tuple, list)):
                    if shape and isinstance(shape[0], (tuple, list)):
                        # Multiple outputs
                        for s in shape:
                            shapes.append(list(s) if s else [])
                    else:
                        shapes.append(list(shape))
        except Exception:
            pass
        return shapes

    def _build_edges(
        self, model: "tf.keras.Model", layer_name_to_id: dict[str, int]
    ) -> list[Edge]:
        """
        Build edges from Keras layer inbound_nodes connections.

        Args:
            model: Keras model.
            layer_name_to_id: Map from layer name to node ID.

        Returns:
            List of Edge objects.
        """
        edges = []
        seen = set()

        try:
            for layer in model.layers:
                target_name = layer.name
                target_id = layer_name_to_id.get(target_name)
                if target_id is None:
                    continue

                # Get inbound nodes (Keras 2.x style)
                inbound = []
                if hasattr(layer, "_inbound_nodes"):
                    for node in layer._inbound_nodes:
                        if hasattr(node, "inbound_layers"):
                            inbound.extend(node.inbound_layers)
                # Keras 3.x style
                if hasattr(layer, "input") and hasattr(layer.input, "_keras_history"):
                    prev_layer = layer.input._keras_history[0]
                    if hasattr(prev_layer, "name"):
                        inbound.append(prev_layer)

                for prev_layer in inbound:
                    if hasattr(prev_layer, "name"):
                        source_id = layer_name_to_id.get(prev_layer.name)
                        if source_id is not None and source_id != target_id:
                            edge_key = (source_id, target_id)
                            if edge_key not in seen:
                                seen.add(edge_key)
                                edges.append(
                                    Edge(
                                        source_id=source_id,
                                        target_id=target_id,
                                        edge_type="sequential",
                                    )
                                )
        except Exception:
            pass

        return edges
