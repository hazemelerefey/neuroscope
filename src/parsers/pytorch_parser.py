"""
PyTorch Model Parser — Parses .pt and .pth files.

Extracts the computation graph from PyTorch models using torch.fx or
manual tracing, then converts to NeuroScopeGraph.
"""

import os
from functools import reduce
from typing import Optional

from src.graph import Edge, LayerNode, NeuroScopeGraph
from src.parsers import BaseParser

# Map PyTorch module types to NeuroScope categories
_MODULE_CATEGORIES = {
    "Conv1d": "convolution",
    "Conv2d": "convolution",
    "Conv3d": "convolution",
    "ConvTranspose1d": "convolution",
    "ConvTranspose2d": "convolution",
    "ConvTranspose3d": "convolution",
    "Linear": "linear",
    "Bilinear": "linear",
    "MaxPool1d": "pooling",
    "MaxPool2d": "pooling",
    "MaxPool3d": "pooling",
    "AvgPool1d": "pooling",
    "AvgPool2d": "pooling",
    "AvgPool3d": "pooling",
    "AdaptiveAvgPool1d": "pooling",
    "AdaptiveAvgPool2d": "pooling",
    "AdaptiveMaxPool1d": "pooling",
    "AdaptiveMaxPool2d": "pooling",
    "GlobalAvgPool": "pooling",
    "BatchNorm1d": "normalization",
    "BatchNorm2d": "normalization",
    "BatchNorm3d": "normalization",
    "LayerNorm": "normalization",
    "GroupNorm": "normalization",
    "InstanceNorm1d": "normalization",
    "InstanceNorm2d": "normalization",
    "InstanceNorm3d": "normalization",
    "SyncBatchNorm": "normalization",
    "ReLU": "activation",
    "LeakyReLU": "activation",
    "GELU": "activation",
    "SiLU": "activation",
    "Sigmoid": "activation",
    "Tanh": "activation",
    "Softmax": "activation",
    "ELU": "activation",
    "SELU": "activation",
    "Mish": "activation",
    "Hardswish": "activation",
    "Hardtanh": "activation",
    "PReLU": "activation",
    "Dropout": "regularization",
    "Dropout2d": "regularization",
    "Dropout3d": "regularization",
    "Flatten": "reshape",
    "Unflatten": "reshape",
    "Reshape": "reshape",
    "LSTM": "recurrent",
    "GRU": "recurrent",
    "RNN": "recurrent",
    "Embedding": "embedding",
    "MultiheadAttention": "attention",
    "Transformer": "attention",
    "TransformerEncoder": "attention",
    "TransformerDecoder": "attention",
    "Add": "combination",
    "Concat": "combination",
}

# Map PyTorch module class names to NeuroScope op_types
_MODULE_TO_OP = {
    "Conv1d": "Conv",
    "Conv2d": "Conv",
    "Conv3d": "Conv",
    "ConvTranspose1d": "ConvTranspose",
    "ConvTranspose2d": "ConvTranspose",
    "ConvTranspose3d": "ConvTranspose",
    "Linear": "Gemm",
    "Bilinear": "Gemm",
    "MaxPool1d": "MaxPool",
    "MaxPool2d": "MaxPool",
    "MaxPool3d": "MaxPool",
    "AvgPool1d": "AveragePool",
    "AvgPool2d": "AveragePool",
    "AvgPool3d": "AveragePool",
    "AdaptiveAvgPool1d": "AdaptiveAveragePool",
    "AdaptiveAvgPool2d": "AdaptiveAveragePool",
    "AdaptiveMaxPool1d": "AdaptiveMaxPool",
    "AdaptiveMaxPool2d": "AdaptiveMaxPool",
    "BatchNorm1d": "BatchNormalization",
    "BatchNorm2d": "BatchNormalization",
    "BatchNorm3d": "BatchNormalization",
    "LayerNorm": "LayerNormalization",
    "GroupNorm": "GroupNormalization",
    "InstanceNorm1d": "InstanceNormalization",
    "InstanceNorm2d": "InstanceNormalization",
    "InstanceNorm3d": "InstanceNormalization",
    "SyncBatchNorm": "BatchNormalization",
    "ReLU": "Relu",
    "LeakyReLU": "LeakyRelu",
    "GELU": "Gelu",
    "SiLU": "Silu",
    "Sigmoid": "Sigmoid",
    "Tanh": "Tanh",
    "Softmax": "Softmax",
    "ELU": "Elu",
    "SELU": "Selu",
    "Mish": "Mish",
    "Hardswish": "Hardswish",
    "Hardtanh": "Relu",
    "PReLU": "PRelu",
    "Dropout": "Dropout",
    "Dropout2d": "Dropout",
    "Dropout3d": "Dropout",
    "Flatten": "Flatten",
    "LSTM": "LSTM",
    "GRU": "GRU",
    "RNN": "RNN",
    "Embedding": "Embedding",
    "MultiheadAttention": "MultiHeadAttention",
    "Transformer": "Attention",
    "TransformerEncoder": "Attention",
    "TransformerDecoder": "Attention",
}

# Educational descriptions
_DESCRIPTIONS = {
    "Conv": "Applies convolutional filters to extract spatial features from input.",
    "Gemm": "Fully connected layer — each output is a weighted sum of all inputs.",
    "Relu": "Rectified Linear Unit — outputs max(0, x). Most common activation.",
    "Gelu": "Gaussian Error Linear Unit — smoother alternative to ReLU.",
    "BatchNormalization": "Normalizes activations across the batch. Stabilizes training.",
    "MaxPool": "Reduces spatial dimensions by taking the maximum in each window.",
    "AveragePool": "Reduces spatial dimensions by averaging values in each window.",
    "Dropout": "Randomly zeros neurons during training. Prevents overfitting.",
    "LSTM": "Long Short-Term Memory — captures long-range dependencies.",
    "GRU": "Gated Recurrent Unit — simplified alternative to LSTM.",
    "MultiHeadAttention": "Attention mechanism — computes weighted relationships between tokens.",
}


class PyTorchParser(BaseParser):
    """Parser for PyTorch model files (.pt, .pth)."""

    def supports(self, file_path: str) -> bool:
        """Check if file has a PyTorch extension."""
        return file_path.lower().endswith((".pt", ".pth"))

    def parse(self, file_path: str, **kwargs) -> NeuroScopeGraph:
        """
        Parse a PyTorch model file into a NeuroScopeGraph.

        Attempts multiple loading strategies:
        1. torch.load → nn.Module → extract modules
        2. Fallback to state_dict inspection

        Args:
            file_path: Path to the .pt/.pth file.
            **kwargs: Optional arguments:
                - device (str): Device to load on (default: "cpu")

        Returns:
            NeuroScopeGraph representation.

        Raises:
            ImportError: If torch is not installed.
            FileNotFoundError: If file doesn't exist.
            ValueError: If file cannot be parsed.
        """
        try:
            import torch
        except ImportError:
            raise ImportError(
                "torch package not installed. Run: pip install torch"
            )

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")

        device = kwargs.get("device", "cpu")

        # Load the object
        try:
            obj = torch.load(file_path, map_location=device, weights_only=False)
        except Exception as e:
            raise ValueError(f"Failed to load PyTorch file: {e}")

        # Determine what we loaded
        import torch.nn as nn

        if isinstance(obj, nn.Module):
            return self._parse_module(obj, file_path)
        elif isinstance(obj, dict):
            return self._parse_state_dict(obj, file_path)
        else:
            raise ValueError(
                f"Unsupported PyTorch object type: {type(obj).__name__}. "
                f"Expected nn.Module or state_dict (OrderedDict)."
            )

    def _parse_module(self, model: "torch.nn.Module", file_path: str) -> NeuroScopeGraph:
        """
        Parse an nn.Module by iterating over named modules.

        Args:
            model: PyTorch nn.Module.
            file_path: Original file path for metadata.

        Returns:
            NeuroScopeGraph.
        """
        nodes = []
        edges = []
        module_list = []

        # Collect all leaf modules (modules with no children, or known atomic ops)
        for name, module in model.named_modules():
            # Skip the root module itself and container modules
            class_name = type(module).__name__
            if class_name in ("Sequential", "ModuleList", "ModuleDict", "Module"):
                continue
            if list(module.children()):
                continue  # Has children, not a leaf

            module_list.append((name, module, class_name))

        # If no leaf modules found, try named_children (one level)
        if not module_list:
            for name, module in model.named_children():
                class_name = type(module).__name__
                module_list.append((name, module, class_name))

        # Build nodes
        for idx, (name, module, class_name) in enumerate(module_list):
            op_type = _MODULE_TO_OP.get(class_name, class_name)
            category = _MODULE_CATEGORIES.get(class_name, "other")
            description = _DESCRIPTIONS.get(op_type, "")

            # Extract attributes
            attributes = self._extract_module_attributes(module, class_name)

            # Count parameters
            params = sum(p.numel() for p in module.parameters())

            # Try to infer output shape from module config
            output_shapes = self._infer_output_shape(module, class_name)

            node = LayerNode(
                id=idx,
                name=name or f"{class_name}_{idx}",
                op_type=op_type,
                category=category,
                input_shapes=[],
                output_shapes=output_shapes,
                attributes=attributes,
                params=params,
                description=description,
            )
            nodes.append(node)

        # Build sequential edges (assuming modules are in execution order)
        for i in range(len(nodes) - 1):
            edges.append(Edge(source_id=i, target_id=i + 1))

        graph = NeuroScopeGraph(
            nodes=nodes,
            edges=edges,
            model_name=os.path.basename(file_path),
            framework="pytorch",
        )
        graph.compute_aggregates()
        return graph

    def _parse_state_dict(self, state_dict: dict, file_path: str) -> NeuroScopeGraph:
        """
        Parse a state_dict (weight dictionary) into a graph.

        Groups weights by layer prefix and infers layer types from
        weight tensor shapes.

        Args:
            state_dict: PyTorch state_dict (OrderedDict of tensors).
            file_path: Original file path for metadata.

        Returns:
            NeuroScopeGraph.
        """
        import re

        # Group keys by layer prefix
        layer_weights: dict[str, list] = {}
        for key, tensor in state_dict.items():
            # Extract layer prefix (e.g., "features.0" from "features.0.weight")
            parts = key.rsplit(".", 1)
            if len(parts) == 2:
                prefix = parts[0]
                suffix = parts[1]
            else:
                prefix = key
                suffix = ""

            if prefix not in layer_weights:
                layer_weights[prefix] = []
            try:
                layer_weights[prefix].append((suffix, tensor.shape if hasattr(tensor, 'shape') else ()))
            except Exception:
                pass

        # Build nodes
        nodes = []
        for idx, (prefix, weights) in enumerate(layer_weights.items()):
            op_type, category = self._infer_layer_type(weights)
            params = sum(
                int(reduce(lambda a, b: a * b, w[1])) if w[1] else 0
                for w in weights
            )

            # Try to get output shape from weight shapes
            output_shapes = []
            for suffix, shape in weights:
                if suffix == "weight" and len(shape) >= 1:
                    output_shapes.append(list(shape))
                    break

            node = LayerNode(
                id=idx,
                name=prefix,
                op_type=op_type,
                category=category,
                input_shapes=[],
                output_shapes=output_shapes,
                attributes={},
                params=params,
            )
            nodes.append(node)

        # Build sequential edges
        edges = []
        for i in range(len(nodes) - 1):
            edges.append(Edge(source_id=i, target_id=i + 1))

        graph = NeuroScopeGraph(
            nodes=nodes,
            edges=edges,
            model_name=os.path.basename(file_path),
            framework="pytorch",
        )
        graph.compute_aggregates()
        return graph

    def _extract_module_attributes(self, module: "torch.nn.Module", class_name: str) -> dict:
        """Extract configuration attributes from a PyTorch module."""
        attrs = {}

        try:
            # Conv layers
            if "Conv" in class_name:
                if hasattr(module, "kernel_size"):
                    attrs["kernel_shape"] = list(module.kernel_size)
                if hasattr(module, "stride"):
                    attrs["strides"] = list(module.stride)
                if hasattr(module, "padding"):
                    attrs["pads"] = list(module.padding)
                if hasattr(module, "dilation"):
                    attrs["dilations"] = list(module.dilation)
                if hasattr(module, "groups"):
                    attrs["group"] = module.groups

            # Pool layers
            elif "Pool" in class_name:
                if hasattr(module, "kernel_size"):
                    ks = module.kernel_size
                    attrs["kernel_shape"] = list(ks) if isinstance(ks, (tuple, list)) else [ks, ks]
                if hasattr(module, "stride"):
                    s = module.stride
                    attrs["strides"] = list(s) if isinstance(s, (tuple, list)) else [s, s]

            # Linear
            elif class_name in ("Linear", "Bilinear"):
                if hasattr(module, "in_features"):
                    attrs["in_features"] = module.in_features
                if hasattr(module, "out_features"):
                    attrs["out_features"] = module.out_features

            # Normalization
            elif "Norm" in class_name or "BatchNorm" in class_name:
                if hasattr(module, "eps"):
                    attrs["epsilon"] = module.eps
                if hasattr(module, "momentum"):
                    attrs["momentum"] = module.momentum
                if hasattr(module, "num_features"):
                    attrs["num_features"] = module.num_features

            # RNN layers
            elif class_name in ("LSTM", "GRU", "RNN"):
                if hasattr(module, "input_size"):
                    attrs["input_size"] = module.input_size
                if hasattr(module, "hidden_size"):
                    attrs["hidden_size"] = module.hidden_size
                if hasattr(module, "num_layers"):
                    attrs["num_layers"] = module.num_layers
                if hasattr(module, "bidirectional"):
                    attrs["bidirectional"] = module.bidirectional

            # Dropout
            elif "Dropout" in class_name:
                if hasattr(module, "p"):
                    attrs["ratio"] = module.p

            # Embedding
            elif class_name == "Embedding":
                if hasattr(module, "num_embeddings"):
                    attrs["vocab_size"] = module.num_embeddings
                if hasattr(module, "embedding_dim"):
                    attrs["embedding_dim"] = module.embedding_dim

            # MultiheadAttention
            elif "Attention" in class_name:
                if hasattr(module, "embed_dim"):
                    attrs["embed_dim"] = module.embed_dim
                if hasattr(module, "num_heads"):
                    attrs["num_heads"] = module.num_heads

        except Exception:
            pass

        return attrs

    def _infer_output_shape(self, module: "torch.nn.Module", class_name: str) -> list[list[int]]:
        """Try to infer output shape from module configuration."""
        shapes = []

        try:
            if class_name in ("Linear", "Bilinear") and hasattr(module, "out_features"):
                shapes.append([-1, module.out_features])
        except Exception:
            pass

        return shapes

    def _infer_layer_type(self, weights: list[tuple]) -> tuple[str, str]:
        """
        Infer layer type from weight tensor shapes.

        Args:
            weights: List of (suffix, shape) tuples.

        Returns:
            (op_type, category) tuple.
        """
        for suffix, shape in weights:
            if suffix == "weight":
                rank = len(shape)
                if rank == 4:
                    return "Conv", "convolution"
                elif rank == 3:
                    return "Conv", "convolution"
                elif rank == 2:
                    return "Gemm", "linear"
                elif rank == 1:
                    # Could be norm bias or 1D conv weight
                    return "BatchNormalization", "normalization"
            elif suffix in ("running_mean", "running_var"):
                return "BatchNormalization", "normalization"

        return "Unknown", "other"

