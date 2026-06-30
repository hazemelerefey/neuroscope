# NeuroScope — Data Science Guide

**For:** Mohamed Abdel Ghani (Data Science)  
**Date:** June 30, 2026  
**Version:** 1.0

---

## Your Role

You own the **intelligence layer** of NeuroScope:
- Model architecture definitions (JSON format)
- Educational content for deep learning topics
- Builder validation rules
- Future model additions (YOLO, ResNet, EfficientNet, classical ML)

---

## 1. Model Definition Format

Every model in NeuroScope is defined as a JSON file in `src/data/models/`. The API automatically discovers any `.json` file in this directory.

### Schema Overview

```json
{
  "id": "cnn_v16",                    // Unique identifier
  "name": "CNN v16",                  // Display name
  "family": "cnn",                    // Model family (grouping key)
  "version": "v16",                   // Version string
  "description": "...",               // Short description
  "sizes": { ... },                   // Optional: size variants
  "layers": [ ... ],                  // Layer definitions
  "head": { ... },                    // Classification head
  "extensions": [ ... ]               // Hyperparameter extensions
}
```

### Layer Format

Each layer in the `layers` array:

```json
{
  "id": "conv1",                      // Unique layer ID
  "type": "conv2d",                   // Layer type (matches 3D shape mapping)
  "name": "Conv2d Block 1",           // Display name
  "params": {                         // Layer parameters
    "in_channels": 3,
    "out_channels": 64,
    "kernel_size": 3,
    "code": "nn.Conv2d(3, 64, kernel_size=3, padding=1)"
  },
  "code": "nn.Conv2d(3, 64, kernel_size=3, padding=1)",  // PyTorch code
  "freezable": true                   // Can user freeze this layer?
}
```

**Supported layer types:**
| Type | 3D Shape | Description |
|------|----------|-------------|
| `conv2d` | Box | Convolutional layer |
| `batchnorm` | Cylinder | Batch normalization |
| `activation` | Sphere | Activation function |
| `pooling` | Flat box | Max/Average pooling |
| `dropout` | Dashed sphere | Dropout |
| `linear` | Plane | Fully connected layer |
| `flatten` | Arrow | Reshape layer |
| `skip` | Curved cable | Skip connection |

### Extension Format

Each extension in the `extensions` array:

```json
{
  "id": "optimizer",                  // Unique extension ID
  "name": "Optimizer",                // Display name
  "category": "training",             // Category (training/functional/data)
  "color": "#f59e0b",                 // UI color (hex)
  "icon": "⚡",                        // UI icon (emoji)
  "options": [                        // Available options
    {
      "id": "adamw",                  // Option ID
      "name": "AdamW",                // Display name
      "code": "optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)",
      "description": "Adam with proper weight decay. Best default for most architectures.",
      "when_to_use": "Use as your default optimizer.",
      "consequences": "Fast convergence. Weight decay provides regularization.",
      "default": true                 // Is this the default option?
    }
  ]
}
```

**Quality standards for educational content:**
- `description`: 1-2 sentences. What it IS.
- `when_to_use`: 1-2 sentences. WHEN to pick this option.
- `consequences`: 1-2 sentences. WHAT HAPPENS if you choose this.
- `code`: Complete PyTorch code line. Must be copy-paste ready.

---

## 2. CNN v16 Reference

The launch model. 16 layers, 7 extensions.

### Layer Breakdown

| # | ID | Type | Channels | Purpose |
|---|-----|------|----------|---------|
| 1 | conv1 | Conv2d | 3→64 | Low-level feature extraction (edges, textures) |
| 2 | bn1 | BatchNorm | 64 | Stabilize activations |
| 3 | relu1 | ReLU | 64 | Non-linearity |
| 4 | conv2 | Conv2d | 64→64 | Feature refinement |
| 5 | bn2 | BatchNorm | 64 | Stabilize |
| 6 | relu2 | ReLU | 64 | Non-linearity |
| 7 | pool1 | MaxPool2d | 64 | Downsample (224→112) |
| 8 | conv3 | Conv2d | 64→128 | Mid-level features |
| 9 | bn3 | BatchNorm | 128 | Stabilize |
| 10 | relu3 | ReLU | 128 | Non-linearity |
| 11 | conv4 | Conv2d | 128→256 | High-level features |
| 12 | bn4 | BatchNorm | 256 | Stabilize |
| 13 | relu4 | ReLU | 256 | Non-linearity |
| 14 | pool2 | MaxPool2d | 256 | Downsample (112→56) |
| 15 | gap | GlobalAvgPool | 256 | Spatial summarization |
| 16 | flatten | Flatten | 256 | Reshape for classifier |

**Head:** `nn.LazyLinear(num_classes)` with Softmax activation.

### Extensions

| Extension | Options | Default |
|-----------|---------|---------|
| ⚡ Optimizer | SGD, Adam, AdamW, RMSprop | AdamW |
| 🔥 Activation | ReLU, LeakyReLU, SiLU, Mish, GELU | ReLU |
| 💚 Loss | CrossEntropy, FocalLoss, LabelSmoothing | CrossEntropy |
| 📈 Learning Rate | 0.1, 0.01, 0.001, 0.0001 | 0.001 |
| 📦 Batch Size | 8, 16, 32, 64, 128 | 32 |
| 🔄 Epochs | 50, 100, 200, 500 | 100 |
| 🟣 Augmentation | None, Basic, Advanced, Custom | Basic |

---

## 3. Adding a New Model

### Step-by-Step

1. **Create the JSON file** in `src/data/models/`:
   ```
   src/data/models/yolo_v11.json
   ```

2. **Define the schema** — follow CNN v16 format:
   ```json
   {
     "id": "yolo_v11",
     "name": "YOLO v11",
     "family": "yolo",
     "version": "v11",
     "description": "You Only Look Once — real-time object detection",
     "sizes": {
       "nano": {"params": "2.6M"},
       "small": {"params": "9.4M"},
       "medium": {"params": "20.1M"},
       "large": {"params": "25.3M"},
       "xlarge": {"params": "56.9M"}
     },
     "layers": [...],
     "head": {...},
     "extensions": [...]
   }
   ```

3. **Define layers** — each layer needs:
   - `id`, `type`, `name`, `params`, `code`, `freezable`
   - Use types from the supported list (conv2d, batchnorm, etc.)
   - For new types, add to `config/layer_shapes.yaml` first

4. **Define extensions** — YOLO-specific:
   - NMS (on/off, IoU threshold) — not needed for CNN
   - Anchor boxes — YOLO-specific
   - Image size — YOLO-specific

5. **Write educational content** — every option needs:
   - `description`: What it is
   - `when_to_use`: When to pick it
   - `consequences`: What happens
   - `code`: PyTorch code

6. **Test** — the API auto-discovers new JSON files:
   ```bash
   curl http://localhost:8000/api/models
   # Should show yolo in the families list
   ```

### Quality Checklist

- [ ] All layers have `code` fields with valid PyTorch
- [ ] All extensions have at least 2 options
- [ ] Every option has `description`, `when_to_use`, `consequences`
- [ ] Default option is marked for each extension
- [ ] `head` defines the classification/detection head
- [ ] Sizes are defined if the model has size variants
- [ ] JSON validates without errors
- [ ] API returns the model correctly

---

## 4. Builder Rules

Validation rules in `config/builder_rules.yaml`. The frontend uses these to warn users about common mistakes.

### Rule Format

```yaml
category_rules:
  rule_name:
    enabled: true
    severity: WARNING  # ERROR, WARNING, INFO
    trigger_condition: value
    message: "Human-readable explanation"
```

### Adding a New Rule

1. Open `config/builder_rules.yaml`
2. Add to the appropriate category (`layer_rules`, `architecture_rules`, `training_rules`)
3. Set severity:
   - **ERROR**: Blocks export (e.g., missing head, invalid architecture)
   - **WARNING**: Shows warning but allows export (e.g., sigmoid in deep net)
   - **INFO**: Informational tip (e.g., consider using BatchNorm)
4. Write a clear message that explains:
   - What the problem is
   - Why it matters
   - What to do instead

### Example: Adding a "no_augmentation" rule

```yaml
training_rules:
  no_augmentation:
    enabled: true
    severity: INFO
    min_dataset_size: 500
    message: "Consider adding data augmentation to prevent overfitting on small datasets."
```

---

## 5. Educational Content

The `/api/educational/{topic}` endpoint serves DL educational content. Currently hardcoded in `src/api/routes/educational.py`.

### Adding a New Topic

1. Open `src/api/routes/educational.py`
2. Add to the `EDUCATIONAL_CONTENT` dictionary:
   ```python
   "new_topic": {
       "title": "Topic Title",
       "summary": "One-line summary",
       "content": "## Markdown content\n\nDetailed explanation...",
       "tips": ["Tip 1", "Tip 2", "Tip 3"]
   }
   ```
3. Content quality standards:
   - `title`: Clear, descriptive
   - `summary`: One sentence, plain language
   - `content`: Markdown format, 200-500 words, include diagrams if possible
   - `tips`: 3-5 actionable tips, each one sentence

### Content Writing Guidelines

- **Audience**: ML students who know Python but are new to DL
- **Language**: Simple, direct, no jargon without explanation
- **Structure**: What → Why → How → When → Tips
- **Tone**: Helpful, not condescending

---

## 6. Future Model Roadmap

| Model | Type | Priority | Complexity |
|-------|------|----------|------------|
| YOLO v11 | Object Detection | High | High — anchor boxes, NMS, multi-scale |
| ResNet-50 | Image Classification | Medium | Medium — skip connections, bottleneck blocks |
| EfficientNet-B0 | Efficient Classification | Medium | Medium — compound scaling, MBConv |
| Decision Tree | Classical ML | Low | Low — sklearn-based |
| Random Forest | Classical ML | Low | Low — ensemble of trees |
| XGBoost | Classical ML | Low | Low — gradient boosting |

---

*Last updated: June 30, 2026*
