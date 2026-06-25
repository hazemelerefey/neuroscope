"""
Memory Footprint Estimator.

Estimates memory usage for:
- Model weights
- Optimizer states (Adam: 2× weights, SGD with momentum: 1× weights)
- Activations (during forward pass)
- Gradients (during training)
"""

from src.graph import LayerNode, NeuroScopeGraph


# Bytes per element for different precision levels
BYTES_PER_ELEMENT = {
    "float32": 4,
    "float16": 2,
    "bfloat16": 2,
    "int8": 1,
    "int4": 0.5,
}


def estimate_memory(
    graph: NeuroScopeGraph,
    precision: str = "float32",
    batch_size: int = 1,
    optimizer: str = "adam",
) -> dict:
    """
    Estimate memory footprint for the model.

    Args:
        graph: The model graph.
        precision: Weight precision ("float32", "float16", "int8").
        batch_size: Batch size for activation memory.
        optimizer: Optimizer type ("adam", "sgd", "none").

    Returns:
        Dictionary with memory breakdown in bytes.
    """
    bpe = BYTES_PER_ELEMENT.get(precision, 4)

    # 1. Weight memory
    weight_memory = sum(n.params for n in graph.nodes) * bpe

    # 2. Gradient memory (same as weights during training)
    gradient_memory = weight_memory

    # 3. Optimizer state memory
    optimizer_memory = 0
    if optimizer == "adam":
        # Adam stores m (first moment) and v (second moment) per parameter
        optimizer_memory = weight_memory * 2
    elif optimizer == "sgd":
        # SGD with momentum stores velocity per parameter
        optimizer_memory = weight_memory

    # 4. Activation memory (approximate)
    activation_memory = 0
    for node in graph.nodes:
        if node.output_shapes:
            shape = node.output_shapes[0]
            if shape and all(s > 0 for s in shape):
                # Replace batch dimension with actual batch size
                act_shape = [batch_size] + shape[1:]
                act_size = 1
                for dim in act_shape:
                    act_size *= dim
                activation_memory += act_size * bpe

    # Total
    total = weight_memory + gradient_memory + optimizer_memory + activation_memory

    return {
        "weights_bytes": weight_memory,
        "gradients_bytes": gradient_memory,
        "optimizer_bytes": optimizer_memory,
        "activations_bytes": activation_memory,
        "total_bytes": total,
        "total_mb": total / (1024 ** 2),
        "total_gb": total / (1024 ** 3),
        # GPU memory estimate (with overhead)
        "gpu_memory_gb": (total * 1.2) / (1024 ** 3),  # 20% overhead
    }


def estimate_training_time(
    graph: NeuroScopeGraph,
    hardware: str = "T4",
    batch_size: int = 32,
    dataset_size: int = 10000,
    epochs: int = 100,
) -> dict:
    """
    Estimate training time based on model architecture and hardware.

    Args:
        graph: The model graph.
        hardware: GPU type ("T4", "V100", "A100", "RTX3090", "CPU").
        batch_size: Training batch size.
        dataset_size: Number of training samples.
        epochs: Number of training epochs.

    Returns:
        Dictionary with time estimates.
    """
    # Hardware FLOPS (approximate, TFLOPS for FP32)
    hardware_flops = {
        "T4": 8.1e12,
        "V100": 15.7e12,
        "A100": 19.5e12,
        "RTX3090": 35.6e12,
        "RTX4090": 82.6e12,
        "CPU": 0.5e12,
    }

    peak_flops = hardware_flops.get(hardware, 8.1e12)

    # Assume ~30% utilization (typical for ML workloads)
    effective_flops = peak_flops * 0.3

    # FLOPs per forward pass
    forward_flops = graph.total_flops

    # Backward pass ≈ 2× forward
    total_flops_per_sample = forward_flops * 3  # forward + backward + update

    # Per epoch
    steps_per_epoch = dataset_size // batch_size
    flops_per_epoch = total_flops_per_sample * dataset_size

    # Total
    total_flops = flops_per_epoch * epochs

    # Time estimate (seconds)
    time_seconds = total_flops / effective_flops

    return {
        "forward_flops": forward_flops,
        "total_flops_per_sample": total_flops_per_sample,
        "steps_per_epoch": steps_per_epoch,
        "total_flops": total_flops,
        "estimated_seconds": time_seconds,
        "estimated_minutes": time_seconds / 60,
        "estimated_hours": time_seconds / 3600,
        "hardware": hardware,
        "effective_tflops": effective_flops / 1e12,
    }
