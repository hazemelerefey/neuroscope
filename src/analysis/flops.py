"""
FLOPs (Floating Point Operations) Calculator.

Computes per-layer and total FLOPs from the model graph.
"""

from src.graph import LayerNode, NeuroScopeGraph


def calculate_flops(graph: NeuroScopeGraph) -> NeuroScopeGraph:
    """
    Calculate FLOPs for each layer in the graph.

    Modifies nodes in-place with flops attribute.
    Returns the graph for chaining.
    """
    for node in graph.nodes:
        node.flops = _calculate_layer_flops(node)

    graph.compute_aggregates()
    return graph


def _calculate_layer_flops(node: LayerNode) -> int:
    """Calculate FLOPs for a single layer."""
    op = node.op_type

    input_shape = node.input_shapes[0] if node.input_shapes else []
    output_shape = node.output_shapes[0] if node.output_shapes else []

    # For ops that only need output shape, skip the empty-input guard
    output_only_ops = {
        "Relu", "LeakyRelu", "Gelu", "Silu", "Sigmoid", "Tanh",
        "Softmax", "Elu", "Selu", "Mish", "Hardswish", "PRelu",
        "Dropout",
    }
    if op not in output_only_ops and (not input_shape or not output_shape):
        return 0

    if op in ("Conv", "ConvTranspose"):
        return _conv_flops(node, input_shape, output_shape)
    elif op in ("MatMul", "Gemm", "FC"):
        return _matmul_flops(input_shape, output_shape)
    elif op in ("BatchNormalization", "LayerNormalization", "InstanceNormalization", "GroupNormalization"):
        return _norm_flops(input_shape)
    elif op in ("MaxPool", "AveragePool"):
        return _pool_flops(input_shape, output_shape, node.attributes.get("kernel_shape"))
    elif op in ("GlobalAveragePool", "GlobalMaxPool"):
        return _global_pool_flops(input_shape)
    elif op in ("Relu", "LeakyRelu", "Gelu", "Silu", "Sigmoid", "Tanh"):
        return _activation_flops(input_shape or output_shape)
    elif op in ("LSTM", "GRU", "RNN"):
        return _rnn_flops(node, input_shape, output_shape)
    else:
        # For most other ops, FLOPs ≈ output size
        if output_shape:
            return _product(output_shape)
        return 0


def _conv_flops(node: LayerNode, input_shape: list, output_shape: list) -> int:
    """FLOPs for convolution: batch × C_out × H_out × W_out × C_in × kH × kW"""
    if len(input_shape) < 4 or len(output_shape) < 4:
        return 0

    batch = output_shape[0]
    c_out = output_shape[1]
    h_out = output_shape[2] if len(output_shape) > 2 else 1
    w_out = output_shape[3] if len(output_shape) > 3 else 1

    kernel = node.attributes.get("kernel_shape", [3, 3])
    c_in = input_shape[1] if len(input_shape) > 1 else 1
    k_h = kernel[0] if len(kernel) > 0 else 1
    k_w = kernel[1] if len(kernel) > 1 else 1

    groups = node.attributes.get("group", 1)

    # Each output element: C_in/groups × kH × kW multiplications + same additions
    flops_per_element = 2 * (c_in // groups) * k_h * k_w
    return batch * c_out * h_out * w_out * flops_per_element


def _matmul_flops(input_shape: list, output_shape: list) -> int:
    """FLOPs for matrix multiplication: 2 × batch × M × K × N"""
    if len(input_shape) < 2 or len(output_shape) < 2:
        return 0

    batch = input_shape[0] if len(input_shape) > 1 else 1
    m = input_shape[-2] if len(input_shape) > 2 else input_shape[0]
    k = input_shape[-1]
    n = output_shape[-1]

    return 2 * batch * m * k * n


def _norm_flops(input_shape: list) -> int:
    """FLOPs for normalization: ~4 × total_elements (mean, var, normalize, scale)"""
    return 4 * _product(input_shape)


def _pool_flops(input_shape: list, output_shape: list, kernel_shape: list = None) -> int:
    """
    FLOPs for pooling: comparison/averaging per output element.

    Args:
        input_shape: Input tensor shape.
        output_shape: Output tensor shape.
        kernel_shape: Pooling kernel size. If None, estimated from
            input/output spatial ratio.
    """
    if kernel_shape and len(kernel_shape) >= 2:
        k_h, k_w = kernel_shape[0], kernel_shape[1]
    elif len(input_shape) >= 4 and len(output_shape) >= 4 and output_shape[2] > 0 and output_shape[3] > 0:
        # Estimate kernel from input/output spatial ratio
        k_h = max(1, input_shape[2] // output_shape[2]) if len(input_shape) > 2 else 2
        k_w = max(1, input_shape[3] // output_shape[3]) if len(input_shape) > 3 else k_h
    else:
        k_h, k_w = 2, 2
    return _product(output_shape) * k_h * k_w


def _global_pool_flops(input_shape: list) -> int:
    """FLOPs for global pooling: sum/compare across spatial dims."""
    return _product(input_shape)


def _activation_flops(input_shape: list) -> int:
    """FLOPs for activation functions: 1 op per element."""
    return _product(input_shape)


def _rnn_flops(node: LayerNode, input_shape: list, output_shape: list) -> int:
    """FLOPs for RNN/LSTM/GRU: gates × matrix ops × timesteps."""
    if len(input_shape) < 2:
        return 0

    batch = input_shape[0]
    seq_len = input_shape[1] if len(input_shape) > 2 else 1
    input_size = input_shape[-1]
    hidden_size = node.attributes.get("hidden_size", input_size)

    # LSTM: 4 gates, each with input_size × hidden_size + bias
    num_gates = 4 if node.op_type == "LSTM" else 3 if node.op_type == "GRU" else 1
    flops_per_step = num_gates * 2 * (input_size + hidden_size) * hidden_size

    return batch * seq_len * flops_per_step


def _product(shape: list) -> int:
    """Calculate product of shape dimensions."""
    result = 1
    for dim in shape:
        if dim > 0:
            result *= dim
    return result
