"""
Educational API Route — Serve educational content for deep learning topics.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Educational content database
EDUCATIONAL_CONTENT: dict[str, dict] = {
    "conv2d": {
        "title": "Convolutional Layers (Conv2d)",
        "summary": "Convolutional layers are the building blocks of CNNs. They apply learnable filters to input feature maps to detect spatial patterns like edges, textures, and shapes.",
        "content": (
            "## How Conv2d Works\n\n"
            "A convolution slides a small filter (kernel) across the input image, computing dot products at each position. "
            "This produces a feature map that highlights where specific patterns occur.\n\n"
            "### Key Parameters\n"
            "- **in_channels**: Number of input channels (e.g., 3 for RGB)\n"
            "- **out_channels**: Number of filters (determines output depth)\n"
            "- **kernel_size**: Size of the sliding window (typically 3×3 or 5×5)\n"
            "- **stride**: Step size of the sliding window\n"
            "- **padding**: Zero-padding around the input borders\n\n"
            "### Why 3×3 Kernels?\n"
            "Two 3×3 convolutions have the same receptive field as one 5×5 but with fewer parameters and more non-linearity."
        ),
        "tips": [
            "Start with 3×3 kernels — they're the sweet spot for most tasks",
            "Use padding=1 to preserve spatial dimensions",
            "Double channels after each pooling layer (64 → 128 → 256)",
        ],
    },
    "batchnorm": {
        "title": "Batch Normalization",
        "summary": "BatchNorm normalizes activations across the batch dimension, stabilizing training and allowing higher learning rates.",
        "content": (
            "## Batch Normalization\n\n"
            "BatchNorm normalizes each feature to have zero mean and unit variance across the mini-batch, "
            "then applies a learnable scale and shift.\n\n"
            "### Benefits\n"
            "- Stabilizes training\n"
            "- Allows higher learning rates\n"
            "- Acts as a regularizer\n"
            "- Reduces internal covariate shift\n\n"
            "### Placement\n"
            "Typically placed **before** the activation function (Conv → BN → Activation)."
        ),
        "tips": [
            "Use BatchNorm after every convolutional layer",
            "Keep batch size ≥ 16 for stable statistics",
            "In evaluation mode, uses running statistics instead of batch statistics",
        ],
    },
    "activation": {
        "title": "Activation Functions",
        "summary": "Activation functions introduce non-linearity into neural networks, enabling them to learn complex patterns.",
        "content": (
            "## Activation Functions\n\n"
            "Without activations, a deep network would collapse into a single linear transformation.\n\n"
            "### Common Choices\n"
            "- **ReLU**: max(0, x) — fast, default choice\n"
            "- **LeakyReLU**: Small slope for negative values — prevents dead neurons\n"
            "- **SiLU/Swish**: x·σ(x) — smooth, used in modern architectures\n"
            "- **GELU**: Used in transformers\n"
            "- **Sigmoid/Tanh**: Avoid in deep networks (vanishing gradients)"
        ),
        "tips": [
            "ReLU is the default — start here",
            "Use LeakyReLU if you observe dead neurons",
            "Avoid Sigmoid in hidden layers of deep networks",
        ],
    },
    "pooling": {
        "title": "Pooling Layers",
        "summary": "Pooling reduces spatial dimensions, decreasing computation and introducing translation invariance.",
        "content": (
            "## Pooling\n\n"
            "Pooling layers downsample feature maps by aggregating local regions.\n\n"
            "### Types\n"
            "- **MaxPool2d**: Takes the maximum value — preserves strong features\n"
            "- **AvgPool2d**: Takes the average — smoother downsampling\n"
            "- **GlobalAveragePool**: Averages the entire feature map — used before classification head\n\n"
            "### When to Pool\n"
            "Typically after each convolutional block to halve spatial dimensions."
        ),
        "tips": [
            "Use 2×2 MaxPool with stride 2 to halve spatial dimensions",
            "GlobalAveragePool is preferred over Flatten + FC for the classification head",
            "Don't pool too aggressively early on — you'll lose spatial information",
        ],
    },
    "dropout": {
        "title": "Dropout",
        "summary": "Dropout randomly zeros neurons during training, preventing co-adaptation and overfitting.",
        "content": (
            "## Dropout\n\n"
            "During training, each neuron has a probability *p* of being set to zero. "
            "This forces the network to learn redundant representations.\n\n"
            "### Usage\n"
            "- Typically p=0.5 after fully connected layers\n"
            "- p=0.1–0.3 after convolutional layers\n"
            "- Disabled during evaluation\n\n"
            "### Why It Works\n"
            "Prevents neurons from co-adapting — each neuron must learn features that are useful on their own."
        ),
        "tips": [
            "Use p=0.5 in the classifier head",
            "Don't use dropout after every layer — it slows convergence",
            "Combine with data augmentation for best regularization",
        ],
    },
    "optimizer": {
        "title": "Optimizers",
        "summary": "Optimizers update model weights to minimize the loss function. Different algorithms have different trade-offs.",
        "content": (
            "## Optimizers\n\n"
            "### SGD with Momentum\n"
            "Classic optimizer. Slow but often generalizes well. Requires learning rate scheduling.\n\n"
            "### Adam\n"
            "Adaptive learning rates per parameter. Fast convergence, good default.\n\n"
            "### AdamW\n"
            "Adam with proper weight decay. Best default for most modern architectures.\n\n"
            "### Learning Rate\n"
            "The most important hyperparameter. Too high → divergence. Too low → slow convergence."
        ),
        "tips": [
            "AdamW with lr=0.001 is a safe default",
            "Use learning rate warmup for large batch sizes",
            "Cosine annealing is a good LR schedule",
        ],
    },
    "loss_function": {
        "title": "Loss Functions",
        "summary": "Loss functions measure how far the model's predictions are from the ground truth.",
        "content": (
            "## Loss Functions\n\n"
            "### Cross-Entropy Loss\n"
            "Standard for multi-class classification. Combines LogSoftmax + NLLLoss.\n\n"
            "### Focal Loss\n"
            "Down-weights easy examples. Great for imbalanced datasets.\n\n"
            "### Label Smoothing\n"
            "Prevents overconfidence. Instead of hard targets [0,0,1,0], uses soft targets."
        ),
        "tips": [
            "CrossEntropyLoss is the default for classification",
            "Use Focal Loss for imbalanced datasets",
            "Label smoothing helps with calibration",
        ],
    },
    "data_augmentation": {
        "title": "Data Augmentation",
        "summary": "Augmentation artificially increases training data diversity by applying random transformations.",
        "content": (
            "## Data Augmentation\n\n"
            "Augmentation prevents overfitting by showing the model different versions of each image.\n\n"
            "### Common Techniques\n"
            "- Random horizontal flip\n"
            "- Random rotation (±15°)\n"
            "- Color jitter (brightness, contrast, saturation)\n"
            "- Random crop and resize\n\n"
            "### Advanced\n"
            "- Mixup: Blend two images\n"
            "- CutMix: Replace patches\n"
            "- AutoAugment: Learned policies"
        ),
        "tips": [
            "Start with basic augmentation (flip + rotation)",
            "Don't augment validation/test sets",
            "Domain-specific: medical images may not benefit from rotation",
        ],
    },
    "skip_connections": {
        "title": "Skip Connections",
        "summary": "Skip connections (residual connections) allow gradients to flow directly through the network, enabling training of very deep models.",
        "content": (
            "## Skip Connections\n\n"
            "Introduced in ResNet, skip connections add the input of a block to its output:\n\n"
            "```\n"
            "output = F(x) + x\n"
            "```\n\n"
            "### Why They Work\n"
            "- Solve the vanishing gradient problem\n"
            "- Allow training of 100+ layer networks\n"
            "- The network only needs to learn the residual (difference)"
        ),
        "tips": [
            "Add skip connections every 2–3 layers in deep networks",
            "Use when network depth exceeds 10 layers",
            "Pre-activation ResNet (BN → Act → Conv) often works better",
        ],
    },
    "learning_rate": {
        "title": "Learning Rate",
        "summary": "The learning rate controls how much weights are updated during training. It's the most important hyperparameter.",
        "content": (
            "## Learning Rate\n\n"
            "### Choosing a Learning Rate\n"
            "- **0.1**: High — for SGD with warmup\n"
            "- **0.01**: Medium — standard for SGD\n"
            "- **0.001**: Default for Adam/AdamW\n"
            "- **0.0001**: Low — for fine-tuning\n\n"
            "### Schedules\n"
            "- Step decay: Reduce by 10× every N epochs\n"
            "- Cosine annealing: Smooth reduction\n"
            "- Warmup: Start low, increase, then decay"
        ),
        "tips": [
            "Start with 0.001 for AdamW",
            "Use learning rate finder to identify optimal range",
            "Always use a schedule — constant LR is suboptimal",
        ],
    },
}


@router.get("/educational/{topic}")
@limiter.limit("60/minute")
async def get_educational_content(request: Request, topic: str):
    """
    Get educational content for a deep learning topic.

    Available topics: conv2d, batchnorm, activation, pooling, dropout,
    optimizer, loss_function, data_augmentation, skip_connections, learning_rate
    """
    topic_lower = topic.lower().replace("-", "_").replace(" ", "_")

    if topic_lower not in EDUCATIONAL_CONTENT:
        available = ", ".join(sorted(EDUCATIONAL_CONTENT.keys()))
        raise HTTPException(
            status_code=404,
            detail=f"Topic '{topic}' not found. Available topics: {available}",
        )

    return EDUCATIONAL_CONTENT[topic_lower]


@router.get("/educational")
@limiter.limit("60/minute")
async def list_topics(request: Request):
    """
    List all available educational topics.
    """
    topics = [
        {"id": key, "title": value["title"], "summary": value["summary"]}
        for key, value in EDUCATIONAL_CONTENT.items()
    ]
    return {"topics": topics, "total": len(topics)}
