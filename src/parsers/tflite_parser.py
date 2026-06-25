"""
TensorFlow Lite Model Parser — Parses .tflite files.

Extracts operators and tensors from TFLite flatbuffer format,
then converts to NeuroScopeGraph.
"""

import os
from typing import Optional

from src.graph import Edge, LayerNode, NeuroScopeGraph
from src.parsers import BaseParser

# TFLite builtin opcode index → name mapping (common opcodes)
# Full list: https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/schema/schema.fbs
_OPCODE_NAMES = {
    0: "ADD",
    1: "AVERAGE_POOL_2D",
    2: "CONCATENATION",
    3: "CONV_2D",
    4: "DEPTHWISE_CONV_2D",
    5: "DEPTH_TO_SPACE",
    6: "DEQUANTIZE",
    7: "EMBEDDING_LOOKUP",
    8: "FLOOR",
    9: "FULLY_CONNECTED",
    12: "L2_NORMALIZATION",
    13: "L2_POOL_2D",
    14: "LOCAL_RESPONSE_NORMALIZATION",
    15: "LOGISTIC",
    17: "MAX_POOL_2D",
    18: "MUL",
    19: "RELU",
    20: "RELU_N1_TO_1",
    21: "RELU6",
    22: "RESHAPE",
    23: "RESIZE_BILINEAR",
    25: "SOFTMAX",
    26: "SPACE_TO_DEPTH",
    27: "SQUEEZE",
    28: "STRIDED_SLICE",
    29: "SUB",
    31: "TRANSPOSE",
    32: "LSTM",
    33: "BIDIRECTIONAL_SEQUENCE_LSTM",
    34: "UNIDIRECTIONAL_SEQUENCE_LSTM",
    37: "TANH",
    38: "CONCAT_EMBEDDINGS",
    39: "SKIP_GRAM",
    42: "CALL",
    43: "CUSTOM",
    44: "EMBEDDING_LOOKUP_SPARSE",
    45: "GATHER",
    46: "BATCH_TO_SPACE_ND",
    47: "SPACE_TO_BATCH_ND",
    48: "TRANSPOSE_CONV",
    49: "MEAN",
    51: "SQUARED_DIFFERENCE",
    52: "SUB",
    54: "COS",
    55: "LESS",
    58: "SPLIT",
    60: "LOG_SOFTMAX",
    61: "CAST",
    62: "PRELU",
    63: "MAXIMUM",
    64: "ARG_MAX",
    65: "MINIMUM",
    66: "LESS_EQUAL",
    67: "GREATER",
    68: "GREATER_EQUAL",
    69: "EQUAL",
    71: "NOT_EQUAL",
    72: "SHAPE",
    73: "POW",
    74: "ARG_MIN",
    75: "FAKE_QUANT",
    76: "REDUCE_PROD",
    77: "REDUCE_MAX",
    78: "PACK",
    79: "LOGICAL_OR",
    80: "ONE_HOT",
    83: "FLOOR_DIV",
    85: "RANK",
    86: "ELU",
    89: "REVERSE_SEQUENCE",
    91: "MATRIX_DIAG",
    93: "REDUCE_MIN",
    95: "FLOOR_MOD",
    96: "RANGE",
    99: "LEAKY_RELU",
    100: "SQUARE_DIFFERENCE",
    102: "ZEROS_LIKE",
    103: "FILL",
    105: "FLOOR_MOD",
    109: "GELU",
    111: "SILU",
    114: "HARD_SWISH",
    116: "DETECTION_POSTPROCESS",
    117: "ABS",
    118: "SPLIT_V",
    119: "UNIQUE",
    121: "CEIL",
    122: "REVERSE_V2",
    127: "ADD_N",
    128: "GATHER_ND",
    129: "WHERE",
    131: "ELU",
    133: "BIDIRECTIONAL_SEQUENCE_RNN",
    134: "UNIDIRECTIONAL_SEQUENCE_RNN",
    136: "BCQ_GATHER",
    137: "BCQ_FULL_CONNECTED",
    138: "INSTANCE_NORM",
}

# TFLite opcode name → NeuroScope category
_OPCODE_CATEGORIES = {
    "CONV_2D": "convolution",
    "DEPTHWISE_CONV_2D": "convolution",
    "TRANSPOSE_CONV": "convolution",
    "FULLY_CONNECTED": "linear",
    "AVERAGE_POOL_2D": "pooling",
    "MAX_POOL_2D": "pooling",
    "L2_POOL_2D": "pooling",
    "RELU": "activation",
    "RELU6": "activation",
    "RELU_N1_TO_1": "activation",
    "LOGISTIC": "activation",
    "TANH": "activation",
    "SOFTMAX": "activation",
    "ELU": "activation",
    "LEAKY_RELU": "activation",
    "PRELU": "activation",
    "GELU": "activation",
    "SILU": "activation",
    "HARD_SWISH": "activation",
    "LOG_SOFTMAX": "activation",
    "L2_NORMALIZATION": "normalization",
    "LOCAL_RESPONSE_NORMALIZATION": "normalization",
    "INSTANCE_NORM": "normalization",
    "RESHAPE": "reshape",
    "SQUEEZE": "reshape",
    "TRANSPOSE": "reshape",
    "SPACE_TO_DEPTH": "reshape",
    "DEPTH_TO_SPACE": "reshape",
    "CONCATENATION": "combination",
    "ADD": "combination",
    "MUL": "combination",
    "SUB": "combination",
    "ADD_N": "combination",
    "SPLIT": "reshape",
    "SPLIT_V": "reshape",
    "PACK": "reshape",
    "LSTM": "recurrent",
    "UNIDIRECTIONAL_SEQUENCE_LSTM": "recurrent",
    "BIDIRECTIONAL_SEQUENCE_LSTM": "recurrent",
    "UNIDIRECTIONAL_SEQUENCE_RNN": "recurrent",
    "BIDIRECTIONAL_SEQUENCE_RNN": "recurrent",
    "EMBEDDING_LOOKUP": "embedding",
    "EMBEDDING_LOOKUP_SPARSE": "embedding",
    "GATHER": "combination",
    "GATHER_ND": "combination",
    "MEAN": "reduction",
    "REDUCE_PROD": "reduction",
    "REDUCE_MAX": "reduction",
    "REDUCE_MIN": "reduction",
    "DEQUANTIZE": "utility",
    "FLOOR": "utility",
    "CEIL": "utility",
    "ABS": "utility",
    "SHAPE": "utility",
    "RANK": "utility",
    "RANGE": "utility",
    "FILL": "utility",
    "ZEROS_LIKE": "utility",
    "WHERE": "utility",
    "LESS": "utility",
    "LESS_EQUAL": "utility",
    "GREATER": "utility",
    "GREATER_EQUAL": "utility",
    "EQUAL": "utility",
    "NOT_EQUAL": "utility",
    "POW": "utility",
    "SQUARE_DIFFERENCE": "utility",
    "CAST": "utility",
    "ONE_HOT": "utility",
    "RESIZE_BILINEAR": "utility",
    "STRIDED_SLICE": "utility",
    "FAKE_QUANT": "utility",
    "CUSTOM": "other",
    "CALL": "other",
}

# TFLite opcode name → NeuroScope op_type
_OPCODE_TO_OP = {
    "CONV_2D": "Conv",
    "DEPTHWISE_CONV_2D": "Conv",
    "TRANSPOSE_CONV": "ConvTranspose",
    "FULLY_CONNECTED": "Gemm",
    "AVERAGE_POOL_2D": "AveragePool",
    "MAX_POOL_2D": "MaxPool",
    "L2_POOL_2D": "AveragePool",
    "RELU": "Relu",
    "RELU6": "Relu",
    "RELU_N1_TO_1": "Relu",
    "LOGISTIC": "Sigmoid",
    "TANH": "Tanh",
    "SOFTMAX": "Softmax",
    "ELU": "Elu",
    "LEAKY_RELU": "LeakyRelu",
    "PRELU": "PRelu",
    "GELU": "Gelu",
    "SILU": "Silu",
    "HARD_SWISH": "Hardswish",
    "LOG_SOFTMAX": "Softmax",
    "L2_NORMALIZATION": "LayerNormalization",
    "LOCAL_RESPONSE_NORMALIZATION": "LayerNormalization",
    "INSTANCE_NORM": "InstanceNormalization",
    "RESHAPE": "Reshape",
    "SQUEEZE": "Squeeze",
    "TRANSPOSE": "Transpose",
    "CONCATENATION": "Concat",
    "ADD": "Add",
    "MUL": "Mul",
    "SUB": "Add",
    "SPLIT": "Reshape",
    "SPLIT_V": "Reshape",
    "PACK": "Reshape",
    "LSTM": "LSTM",
    "UNIDIRECTIONAL_SEQUENCE_LSTM": "LSTM",
    "BIDIRECTIONAL_SEQUENCE_LSTM": "LSTM",
    "UNIDIRECTIONAL_SEQUENCE_RNN": "RNN",
    "BIDIRECTIONAL_SEQUENCE_RNN": "RNN",
    "EMBEDDING_LOOKUP": "Embedding",
    "EMBEDDING_LOOKUP_SPARSE": "Embedding",
    "GATHER": "Concat",
    "MEAN": "ReduceMean",
    "REDUCE_PROD": "ReduceProd",
    "REDUCE_MAX": "ReduceMax",
    "REDUCE_MIN": "ReduceMin",
    "DEQUANTIZE": "Clip",
    "FLOOR": "Clip",
    "CEIL": "Clip",
}

_DESCRIPTIONS = {
    "Conv": "Applies convolutional filters to extract spatial features.",
    "Gemm": "Fully connected layer. Each output is a weighted sum of all inputs.",
    "Relu": "Rectified Linear Unit — outputs max(0, x).",
    "Sigmoid": "Maps values to (0, 1). Used in output layers.",
    "Tanh": "Maps values to (-1, 1).",
    "Softmax": "Converts logits to probabilities for classification.",
    "MaxPool": "Reduces spatial dimensions by taking maximum in each window.",
    "AveragePool": "Reduces spatial dimensions by averaging values.",
    "Reshape": "Reshapes tensor without changing data.",
    "Concat": "Concatenates tensors along a dimension.",
    "Add": "Element-wise addition. Used in residual connections.",
    "LSTM": "Long Short-Term Memory — captures long-range dependencies.",
}


class TFLiteParser(BaseParser):
    """Parser for TensorFlow Lite model files (.tflite)."""

    def supports(self, file_path: str) -> bool:
        """Check if file has a TFLite extension."""
        return file_path.lower().endswith(".tflite")

    def parse(self, file_path: str, **kwargs) -> NeuroScopeGraph:
        """
        Parse a TFLite file into a NeuroScopeGraph.

        Uses the flatbuffers library to read the TFLite schema directly,
        with a fallback to struct-based parsing.

        Args:
            file_path: Path to the .tflite file.
            **kwargs: Optional arguments (currently unused).

        Returns:
            NeuroScopeGraph representation.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file cannot be parsed.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")

        # Try flatbuffers-based parsing first
        try:
            return self._parse_with_flatbuffers(file_path)
        except ImportError:
            pass

        # Fallback: try struct-based parsing
        try:
            return self._parse_with_struct(file_path)
        except Exception:
            pass

        # Last resort: try loading with TensorFlow
        try:
            return self._parse_with_tf(file_path)
        except ImportError:
            raise ValueError(
                "Cannot parse TFLite file. Install one of:\n"
                "  pip install flatbuffers\n"
                "  pip install tensorflow"
            )

    def _parse_with_flatbuffers(self, file_path: str) -> NeuroScopeGraph:
        """
        Parse using the flatbuffers TFLite schema.

        Args:
            file_path: Path to the .tflite file.

        Returns:
            NeuroScopeGraph.
        """
        try:
            from flatbuffers import Builder
        except ImportError:
            raise ImportError("flatbuffers not installed")

        # Read the binary file
        with open(file_path, "rb") as f:
            data = f.read()

        # Parse using struct-based approach (flatbuffers is complex,
        # so we use a simplified binary parser)
        return self._parse_binary(data, file_path)

    def _parse_with_struct(self, file_path: str) -> NeuroScopeGraph:
        """
        Parse using struct module (no external dependencies).

        Args:
            file_path: Path to the .tflite file.

        Returns:
            NeuroScopeGraph.
        """
        with open(file_path, "rb") as f:
            data = f.read()

        return self._parse_binary(data, file_path)

    def _parse_with_tf(self, file_path: str) -> NeuroScopeGraph:
        """
        Parse using TensorFlow Lite interpreter.

        Args:
            file_path: Path to the .tflite file.

        Returns:
            NeuroScopeGraph.
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise ImportError("tensorflow not installed")

        interpreter = tf.lite.Interpreter(model_path=file_path)
        interpreter.allocate_tensors()

        # Get tensor details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Get op details from the model
        op_details = interpreter._get_ops_details() if hasattr(interpreter, '_get_ops_details') else []

        nodes = []
        edges = []
        tensor_to_node: dict[int, int] = {}

        for idx, op in enumerate(op_details):
            op_name = op.get("op_name", "CUSTOM")
            category = _OPCODE_CATEGORIES.get(op_name, "other")
            op_type = _OPCODE_TO_OP.get(op_name, op_name)
            description = _DESCRIPTIONS.get(op_type, "")

            # Get input/output tensor indices
            inputs = op.get("inputs", [])
            outputs = op.get("outputs", [])

            # Get shapes from tensor details
            input_shapes = []
            for inp_idx in inputs:
                try:
                    detail = interpreter._get_tensor_details(inp_idx)
                    if detail and "shape" in detail:
                        input_shapes.append(list(detail["shape"]))
                except Exception:
                    pass

            output_shapes = []
            for out_idx in outputs:
                try:
                    detail = interpreter._get_tensor_details(out_idx)
                    if detail and "shape" in detail:
                        output_shapes.append(list(detail["shape"]))
                except Exception:
                    pass

            # Count parameters (weights)
            params = 0
            for inp_idx in inputs:
                try:
                    detail = interpreter._get_tensor_details(inp_idx)
                    if detail and "shape" in detail:
                        shape = detail["shape"]
                        if len(shape) > 1:  # Likely a weight tensor
                            prod = 1
                            for s in shape:
                                prod *= max(1, s)
                            params += prod
                except Exception:
                    pass

            node = LayerNode(
                id=idx,
                name=op.get("custom_op_name", f"{op_name}_{idx}"),
                op_type=op_type,
                category=category,
                input_shapes=input_shapes,
                output_shapes=output_shapes,
                attributes={},
                params=params,
                description=description,
            )
            nodes.append(node)

            # Track tensor → node mapping for edges
            for out_idx in outputs:
                tensor_to_node[out_idx] = idx

        # Build edges
        for idx, op in enumerate(op_details):
            for inp_idx in op.get("inputs", []):
                if inp_idx in tensor_to_node:
                    source_id = tensor_to_node[inp_idx]
                    if source_id != idx:
                        edges.append(Edge(source_id=source_id, target_id=idx))

        graph = NeuroScopeGraph(
            nodes=nodes,
            edges=edges,
            model_name=os.path.basename(file_path),
            framework="tflite",
        )
        graph.compute_aggregates()
        return graph

    def _parse_binary(self, data: bytes, file_path: str) -> NeuroScopeGraph:
        """
        Parse TFLite binary format directly.

        TFLite uses flatbuffers. This is a simplified parser that
        extracts the operator codes and subgraph structure.

        Args:
            data: Raw bytes of the .tflite file.
            file_path: Original file path for metadata.

        Returns:
            NeuroScopeGraph.
        """
        import struct

        # TFLite flatbuffer root table offset
        if len(data) < 8:
            raise ValueError("Invalid TFLite file: too small")

        # Read root table offset (first 4 bytes, little-endian)
        root_offset = struct.unpack_from("<I", data, 0)[0]

        # Read the buffer size from the root table
        # TFLite Model table has: version, operator_codes, subgraphs, buffers, ...
        # We need to navigate the flatbuffer structure

        # Simplified approach: scan for known patterns and extract opcodes
        # This is a best-effort parser for when flatbuffers/TF aren't available

        nodes = []
        edges = []

        # Try to extract operator codes from the binary
        # The TFLite format stores operator codes as a vector
        opcodes = self._extract_opcodes_from_binary(data)

        if not opcodes:
            # If we can't parse opcodes, create a single "model" node
            nodes.append(
                LayerNode(
                    id=0,
                    name="tflite_model",
                    op_type="Unknown",
                    category="other",
                    description="TFLite model (could not parse individual operators)",
                )
            )
        else:
            # Create a node for each operator
            for idx, opcode_idx in enumerate(opcodes):
                op_name = _OPCODE_NAMES.get(opcode_idx, f"OP_{opcode_idx}")
                category = _OPCODE_CATEGORIES.get(op_name, "other")
                op_type = _OPCODE_TO_OP.get(op_name, op_name)
                description = _DESCRIPTIONS.get(op_type, "")

                node = LayerNode(
                    id=idx,
                    name=f"{op_name}_{idx}",
                    op_type=op_type,
                    category=category,
                    description=description,
                )
                nodes.append(node)

            # Build sequential edges
            for i in range(len(nodes) - 1):
                edges.append(Edge(source_id=i, target_id=i + 1))

        graph = NeuroScopeGraph(
            nodes=nodes,
            edges=edges,
            model_name=os.path.basename(file_path),
            framework="tflite",
        )
        graph.compute_aggregates()
        return graph

    def _extract_opcodes_from_binary(self, data: bytes) -> list[int]:
        """
        Extract operator code indices from TFLite binary.

        This uses heuristics to find the operator_codes vector
        in the flatbuffer.

        Args:
            data: Raw TFLite bytes.

        Returns:
            List of opcode indices.
        """
        import struct

        opcodes = []

        # TFLite files start with a flatbuffer root offset
        if len(data) < 16:
            return opcodes

        try:
            root_offset = struct.unpack_from("<I", data, 0)[0]

            # The Model table starts at root_offset
            # Read vtable offset
            vtable_offset = struct.unpack_from("<i", data, root_offset)[0]
            vtable_pos = root_offset - vtable_offset

            # Read vtable size and object size
            vtable_size = struct.unpack_from("<H", data, vtable_pos)[0]
            object_size = struct.unpack_from("<H", data, vtable_pos + 2)[0]

            # The operator_codes field is typically at offset 4 in the Model table
            # (field index 1: version=0, operator_codes=1, subgraphs=2, ...)
            # Read field offset from vtable
            if vtable_pos + 4 + 2 <= len(data):
                codes_field_offset = struct.unpack_from(
                    "<H", data, vtable_pos + 4 + 2
                )[0]
                if codes_field_offset > 0:
                    codes_vector_pos = root_offset + codes_field_offset
                    # Read vector length
                    if codes_vector_pos + 4 <= len(data):
                        codes_length = struct.unpack_from(
                            "<I", data, codes_vector_pos
                        )[0]
                        # Read each opcode (each is a table with a 'deprecated_builtin_code' field)
                        for i in range(min(codes_length, 200)):  # Sanity limit
                            elem_offset = struct.unpack_from(
                                "<I", data, codes_vector_pos + 4 + i * 4
                            )[0]
                            elem_pos = codes_vector_pos + 4 + i * 4 - elem_offset
                            if elem_pos + 4 <= len(data):
                                # Read deprecated_builtin_code (int8 at offset 4)
                                if elem_pos + 4 + 1 <= len(data):
                                    code = struct.unpack_from(
                                        "<b", data, elem_pos + 4
                                    )[0]
                                    opcodes.append(code & 0xFF)
        except (struct.error, IndexError):
            pass

        return opcodes
