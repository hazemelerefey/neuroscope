"""
ONNX Model Parser — Primary parser for NeuroScope.

Parses .onnx files using the ONNX protobuf schema to extract:
- Layer graph (nodes + edges)
- Layer types and attributes
- Tensor shapes
- Weight information

This is the universal parser — PyTorch and Keras models can be
exported to ONNX first, then parsed here.
"""

import os
from typing import Optional

import numpy as np

try:
    import onnx
    from onnx import numpy_helper, shape_inference
except ImportError:
    onnx = None

from src.graph import Edge, LayerNode, NeuroScopeGraph
from src.parsers import BaseParser

# ONNX op_type → NeuroScope category mapping
OP_CATEGORIES = {
    # Convolution
    "Conv": "convolution",
    "ConvTranspose": "convolution",
    "QLinearConv": "convolution",
    # Pooling
    "MaxPool": "pooling",
    "AveragePool": "pooling",
    "GlobalAveragePool": "pooling",
    "GlobalMaxPool": "pooling",
    "AdaptiveAveragePool": "pooling",
    "AdaptiveMaxPool": "pooling",
    # Linear / Matrix
    "MatMul": "linear",
    "Gemm": "linear",
    "FC": "linear",
    # Activation
    "Relu": "activation",
    "LeakyRelu": "activation",
    "Gelu": "activation",
    "Silu": "activation",
    "Sigmoid": "activation",
    "Tanh": "activation",
    "Softmax": "activation",
    "Elu": "activation",
    "Selu": "activation",
    "Mish": "activation",
    "Hardswish": "activation",
    "HardSigmoid": "activation",
    "PRelu": "activation",
    # Normalization
    "BatchNormalization": "normalization",
    "InstanceNormalization": "normalization",
    "LayerNormalization": "normalization",
    "GroupNormalization": "normalization",
    # Reshape
    "Flatten": "reshape",
    "Reshape": "reshape",
    "Squeeze": "reshape",
    "Unsqueeze": "reshape",
    "Transpose": "reshape",
    # Concat / Split
    "Concat": "combination",
    "Add": "combination",
    "Mul": "combination",
    # Recurrent
    "LSTM": "recurrent",
    "GRU": "recurrent",
    "RNN": "recurrent",
    # Attention
    "Attention": "attention",
    "MultiHeadAttention": "attention",
    # Reduce
    "ReduceMean": "reduction",
    "ReduceSum": "reduction",
    "ReduceMax": "reduction",
    # Other
    "Dropout": "regularization",
    "Clip": "utility",
    "Pad": "utility",
    "Resize": "utility",
}

# Layer descriptions for educational purposes
LAYER_DESCRIPTIONS = {
    "Conv": "Applies convolutional filters to extract spatial features from input. Learns patterns like edges, textures, and shapes.",
    "MatMul": "Matrix multiplication — the core operation of fully connected (dense) layers. Each output is a weighted sum of all inputs.",
    "Gemm": "General matrix multiplication with bias. Used in fully connected layers.",
    "Relu": "Rectified Linear Unit — outputs max(0, x). The most common activation function. Introduces non-linearity.",
    "Gelu": "Gaussian Error Linear Unit — smoother alternative to ReLU, used in transformers.",
    "Sigmoid": "Maps values to (0, 1). Can cause vanishing gradients in deep networks.",
    "Tanh": "Maps values to (-1, 1). Can cause vanishing gradients in deep networks.",
    "Softmax": "Converts logits to probabilities. Used in the final layer for classification.",
    "BatchNormalization": "Normalizes activations across the batch. Stabilizes and accelerates training.",
    "LayerNormalization": "Normalizes across features. Common in transformers.",
    "MaxPool": "Reduces spatial dimensions by taking the maximum value in each window.",
    "AveragePool": "Reduces spatial dimensions by averaging values in each window.",
    "GlobalAveragePool": "Averages each feature map to a single value. Often used before the final classifier.",
    "Flatten": "Reshapes multi-dimensional tensor to 1D. Bridges conv layers and dense layers.",
    "Dropout": "Randomly zeros out neurons during training. Prevents overfitting.",
    "LSTM": "Long Short-Term Memory — recurrent layer that captures long-range dependencies in sequences.",
    "GRU": "Gated Recurrent Unit — simplified alternative to LSTM.",
    "Concat": "Concatenates tensors along a dimension. Used in skip connections and feature merging.",
    "Add": "Element-wise addition. Used in residual/skip connections.",
}


class ONNXParser(BaseParser):
    """Parser for ONNX model files."""

    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith(".onnx")

    def parse(self, file_path: str, **kwargs) -> NeuroScopeGraph:
        """
        Parse an ONNX file into a NeuroScopeGraph.

        Args:
            file_path: Path to the .onnx file.
            **kwargs: Optional arguments:
                - infer_shapes (bool): Run shape inference (default: True)

        Returns:
            NeuroScopeGraph representation.
        """
        if onnx is None:
            raise ImportError("onnx package not installed. Run: pip install onnx")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")

        infer_shapes = kwargs.get("infer_shapes", True)

        # Load model
        model = onnx.load(file_path)

        # Run shape inference if requested
        if infer_shapes:
            try:
                model = shape_inference.infer_shapes(model)
            except Exception:
                pass  # Continue without shape inference

        graph_proto = model.graph

        # Build tensor shape map (from inputs, outputs, value_info)
        tensor_shapes = self._build_shape_map(graph_proto)

        # Build weight map (from initializers)
        weight_map = self._build_weight_map(graph_proto)

        # Parse nodes
        nodes = []
        tensor_producers = {}  # tensor_name → node_id

        for i, node_proto in enumerate(graph_proto.node):
            # Determine category
            category = OP_CATEGORIES.get(node_proto.op_type, "other")

            # Get input/output shapes
            input_shapes = []
            for inp in node_proto.input:
                if inp in tensor_shapes:
                    input_shapes.append(tensor_shapes[inp])

            output_shapes = []
            for out in node_proto.output:
                if out in tensor_shapes:
                    output_shapes.append(tensor_shapes[out])

            # Extract attributes
            attributes = {}
            for attr in node_proto.attribute:
                if attr.type == onnx.AttributeProto.INT:
                    attributes[attr.name] = attr.i
                elif attr.type == onnx.AttributeProto.INTS:
                    attributes[attr.name] = list(attr.ints)
                elif attr.type == onnx.AttributeProto.FLOAT:
                    attributes[attr.name] = attr.f
                elif attr.type == onnx.AttributeProto.FLOATS:
                    attributes[attr.name] = list(attr.floats)
                elif attr.type == onnx.AttributeProto.STRING:
                    attributes[attr.name] = attr.s.decode("utf-8")

            # Calculate params from weights
            params = 0
            for inp in node_proto.input:
                if inp in weight_map:
                    params += weight_map[inp].size

            # Get description
            description = LAYER_DESCRIPTIONS.get(node_proto.op_type, "")

            node = LayerNode(
                id=i,
                name=node_proto.name or f"{node_proto.op_type}_{i}",
                op_type=node_proto.op_type,
                category=category,
                input_shapes=input_shapes,
                output_shapes=output_shapes,
                attributes=attributes,
                params=params,
                description=description,
            )
            nodes.append(node)

            # Track tensor producers for edge detection
            for out in node_proto.output:
                tensor_producers[out] = i

        # Build edges from tensor connections
        edges = self._build_edges(graph_proto, tensor_producers)

        # Create graph
        graph = NeuroScopeGraph(
            nodes=nodes,
            edges=edges,
            model_name=os.path.basename(file_path),
            framework="onnx",
        )
        graph.compute_aggregates()

        return graph

    def _build_shape_map(self, graph_proto) -> dict:
        """Build a map of tensor_name → shape."""
        shapes = {}

        # From graph inputs
        for inp in graph_proto.input:
            shape = self._extract_shape(inp)
            if shape:
                shapes[inp.name] = shape

        # From graph outputs
        for out in graph_proto.output:
            shape = self._extract_shape(out)
            if shape:
                shapes[out.name] = shape

        # From value_info (intermediate tensors)
        for vi in graph_proto.value_info:
            shape = self._extract_shape(vi)
            if shape:
                shapes[vi.name] = shape

        return shapes

    def _extract_shape(self, value_info) -> Optional[list[int]]:
        """Extract shape from a ValueInfoProto."""
        try:
            shape = []
            for dim in value_info.type.tensor_type.shape.dim:
                if dim.dim_value > 0:
                    shape.append(dim.dim_value)
                else:
                    shape.append(-1)  # Dynamic dimension
            return shape if shape else None
        except Exception:
            return None

    def _build_weight_map(self, graph_proto) -> dict:
        """Build a map of tensor_name → numpy array."""
        weights = {}
        for initializer in graph_proto.initializer:
            try:
                weights[initializer.name] = numpy_helper.to_array(initializer)
            except Exception:
                pass
        return weights

    def _build_edges(self, graph_proto, tensor_producers: dict) -> list:
        """Build edges from tensor connections between nodes."""
        edges = []
        seen = set()

        for i, node_proto in enumerate(graph_proto.node):
            for inp in node_proto.input:
                if inp in tensor_producers:
                    source_id = tensor_producers[inp]
                    if source_id != i:  # Skip self-loops
                        edge_key = (source_id, i)
                        if edge_key not in seen:
                            seen.add(edge_key)

                            # Determine edge type
                            edge_type = "sequential"
                            if node_proto.op_type in ("Add", "Concat"):
                                edge_type = "residual"

                            edges.append(
                                Edge(
                                    source_id=source_id,
                                    target_id=i,
                                    edge_type=edge_type,
                                )
                            )

        return edges
