# NeuroScope Data Science Guide

**Track Owner:** Mohamed Abdel Ghani
**Last Updated:** 2026-06-30

---

## Table of Contents

1. [Role Overview](#1-role-overview)
2. [Model Definition Format](#2-model-definition-format)
3. [CNN v16 Reference](#3-cnn-v16-reference)
4. [Educational Content Guide](#4-educational-content-guide)
5. [Builder Rules Guide](#5-builder-rules-guide)
6. [Adding a New Model](#6-adding-a-new-model)
7. [Content Quality Standards](#7-content-quality-standards)

---

## 1. Role Overview

The Data Science track owns everything that defines *what models exist*, *how they work*, and *what users learn* in NeuroScope.

### What We Own

| Area | Files | Responsibility |
|------|-------|----------------|
| **Model architectures** | `src/data/models/*.json` | Define every model family in JSON format |
| **Educational content** | `src/api/routes/educational.py` | DL topic explanations served via API |
| **Builder validation rules** | `config/builder_rules.yaml` | Warn users about bad architecture choices |
| **3D shape mapping** | `config/layer_shapes.yaml` | How layers render in the visual builder |
| **Future model additions** | New JSON files | YOLO, ResNet, EfficientNet, classical ML |

### What We Don't Own

- Frontend rendering (UI track)
- API infrastructure and deployment (Backend track)
- 3D canvas rendering logic (3D/Visual track)
- User authentication and project management (Platform track)

### Collaboration Boundaries

- **With UI:** We provide the JSON schema; they render it visually.
- **With 3D:** We define `layer_shapes.yaml` mappings; they implement the geometry.
- **With Backend:** We provide educational content; they serve it via `/api/educational`.

---

## 2. Model Definition Format

Every model in NeuroScope is defined as a JSON file in `src/data/models/`. The file follows a strict schema.

### 2.1 Top-Level Schema

```json
{
  "id": "cnn_v16",           // Unique identifier (snake_case)
  "name": "CNN v16",         // Display name
  "family": "CNN",           // Model family (CNN, YOLO, ResNet, etc.)
  "version": "16",           // Version string
  "description": "...",      // Human-readable description (1-2 sentences)
  "sizes": null,             // Size variants (null = single size, or object with presets)
  "layers": [],              // Ordered array of layer definitions
  "head": {},                // Classification/detection head
  "extensions": []           // Configurable training extensions
}
```

#### Field Details

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | Yes | Unique snake_case identifier. Used as key in API responses and database references. |
| `name` | `string` | Yes | Human-readable display name shown in the UI. |
| `family` | `string` | Yes | Model family grouping. Groups related architectures (e.g., all CNN variants share `family: "CNN"`). |
| `version` | `string` | Yes | Version identifier. Can be numeric (`"16"`) or semantic (`"v2-large"`). |
| `description` | `string` | Yes | 1-2 sentence summary of the architecture and its purpose. |
| `sizes` | `object\|null` | Yes | Size presets. `null` for single-size models. For models with size variants (e.g., YOLO-nano/small/medium), use an object. |
| `layers` | `array` | Yes | Ordered array of layer objects. The order defines the forward pass sequence. |
| `head` | `object` | Yes | The final layer (classification head, detection head, etc.). Rendered separately from the main layer stack. |
| `extensions` | `array` | Yes | Configurable training extensions (optimizer, loss, augmentation, etc.). |

#### Size Variants (when applicable)

For models that come in multiple sizes:

```json
{
  "sizes": {
    "nano": { "multiplier": 0.25, "description": "Ultra-lightweight for edge devices" },
    "small": { "multiplier": 0.5, "description": "Balanced speed and accuracy" },
    "medium": { "multiplier": 1.0, "description": "Standard size" },
    "large": { "multiplier": 1.5, "description": "Maximum accuracy" }
  }
}
```

### 2.2 Layer Format

Each layer object has this structure:

```json
{
  "id": "conv1",
  "type": "conv2d",
  "name": "Conv2d_1",
  "params": { "in_channels": 3, "out_channels": 64, "kernel_size": 3, "padding": 1 },
  "code": "nn.Conv2d(3, 64, kernel_size=3, padding=1)",
  "freezable": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | Yes | Unique identifier within the model. Short, descriptive (`conv1`, `bn1`, `pool1`). |
| `type` | `string` | Yes | Layer type. Must match a key in `layer_shapes.yaml` for 3D rendering. Common types: `conv2d`, `linear`, `batchnorm`, `activation`, `maxpool`, `avgpool`, `dropout`, `flatten`, `globalavgpool`. |
| `name` | `string` | Yes | Display name shown in the builder UI. Follows pattern: `{Type}_{index}` (e.g., `Conv2d_1`, `BatchNorm_3`). |
| `params` | `object` | Yes | Layer constructor parameters. Keys must match the PyTorch constructor argument names. |
| `code` | `string` | Yes | Exact PyTorch code snippet. Must be valid Python that can be copy-pasted into a training script. |
| `freezable` | `boolean` | Yes | Whether this layer's weights can be frozen during transfer learning. `true` for layers with learnable parameters (Conv, Linear, BatchNorm). `false` for parameterless layers (Activation, Pool, Flatten, Dropout). |

#### Supported Layer Types

| Type | Category | Geometry | Description |
|------|----------|----------|-------------|
| `conv2d` | Core | Box | 2D convolutional layer |
| `conv1d` | Core | Box | 1D convolutional layer |
| `linear` | Core | Plane | Fully connected / dense layer |
| `batchnorm` | Normalization | Slab | Batch normalization |
| `layernorm` | Normalization | Slab | Layer normalization (for transformers) |
| `activation` | Core | Sphere | Activation function (ReLU, GELU, etc.) |
| `maxpool` | Pooling | Small Cube | Max pooling |
| `avgpool` | Pooling | Small Cube | Average pooling |
| `globalavgpool` | Pooling | Small Cube | Global average pooling |
| `dropout` | Regularization | Wireframe | Dropout |
| `flatten` | Reshape | Cone | Flatten spatial dims to vector |
| `lstm` | Recurrent | Cylinder | LSTM layer |
| `gru` | Recurrent | Cylinder | GRU layer |
| `attention` | Attention | Octahedron | Multi-head attention |
| `add` | Combination | Merge | Element-wise addition (skip connections) |
| `concat` | Combination | Merge | Channel concatenation |

### 2.3 Head Format

The `head` field defines the final output layer. It's separate from `layers` because it adapts to the number of classes at runtime.

```json
{
  "id": "head",
  "type": "linear",
  "name": "Classification Head",
  "activation": "softmax",
  "output_neurons": "num_classes",
  "code": "nn.Linear(256, num_classes)",
  "activation_code": "nn.Softmax(dim=1)",
  "description": "The classification head — outputs probability for each class.",
  "freezable": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `activation` | `string` | Final activation function (`softmax`, `sigmoid`, `none`). |
| `output_neurons` | `string` | Output size. Usually `"num_classes"` (runtime variable), but can be fixed (e.g., `"1"` for binary). |
| `activation_code` | `string` | PyTorch code for the activation function. |

### 2.4 Extension Format

Extensions are configurable training hyperparameters that the user can tune.

```json
{
  "id": "optimizer",
  "name": "Optimizer",
  "category": "training",
  "color": "green",
  "icon": "⚡",
  "options": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier. |
| `name` | `string` | Display name. |
| `category` | `string` | Category for grouping: `training`, `functional`, or `data`. |
| `color` | `string` | UI color token: `green` (training), `yellow` (functional), `purple` (data). |
| `icon` | `string` | Emoji icon for the extension. |
| `options` | `array` | Array of option objects (see below). |

#### Extension Option Format

Each option within an extension:

```json
{
  "id": "adamw",
  "name": "AdamW",
  "code": "optimizer = optim.AdamW(model.parameters(), lr={lr}, weight_decay=0.01)",
  "description": "Adam with decoupled weight decay — fixes Adam's incorrect weight decay implementation.",
  "when_to_use": "Best choice for most modern deep learning architectures. Default recommendation.",
  "consequences": "Slightly more computation than vanilla Adam. Weight decay value needs to be tuned.",
  "default": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique option identifier within the extension. |
| `name` | `string` | Display name. |
| `code` | `string` | PyTorch code snippet. Use `{lr}` and other placeholders for values set by other extensions. |
| `description` | `string` | What this option is. 1-2 sentences, plain language. |
| `when_to_use` | `string` | Practical guidance on when to choose this option. |
| `consequences` | `string` | What happens if you choose this — trade-offs, risks, caveats. |
| `default` | `boolean` | Whether this is the default option. Exactly one option per extension should be `true`. |

### 2.5 Adding a New Model Family

To add a completely new model family (e.g., YOLO, ResNet):

1. **Create the JSON file:** `src/data/models/{family}_{version}.json`
2. **Follow the schema** above — fill every required field
3. **Add layer type mappings** in `layer_shapes.yaml` if the model uses layer types not already defined
4. **Add builder rules** in `builder_rules.yaml` if the architecture has common pitfalls
5. **Add educational content** in `educational.py` for any new layer types or concepts
6. **Test** that the 3D builder renders correctly with the new model

---

## 3. CNN v16 Reference

The CNN v16 is NeuroScope's reference architecture — a 16-layer convolutional neural network for image classification. It demonstrates the standard patterns used in the builder.

### 3.1 Architecture Overview

The model has **28 layers** (not counting the head), organized into three convolutional blocks followed by a classification head.

```
Input (3×H×W)
├── Block 1: 64 channels
│   ├── Conv2d_1 (3→64, 3×3)
│   ├── BatchNorm_1
│   ├── Activation_1 (ReLU)
│   ├── Conv2d_2 (64→64, 3×3)
│   ├── BatchNorm_2
│   ├── Activation_2 (ReLU)
│   └── MaxPool_1 (2×2)
├── Block 2: 128 channels
│   ├── Conv2d_3 (64→128, 3×3)
│   ├── BatchNorm_3
│   ├── Activation_3 (ReLU)
│   ├── Conv2d_4 (128→128, 3×3)
│   ├── BatchNorm_4
│   ├── Activation_4 (ReLU)
│   └── MaxPool_2 (2×2)
├── Block 3: 256 channels
│   ├── Conv2d_5 (128→256, 3×3)
│   ├── BatchNorm_5
│   ├── Activation_5 (ReLU)
│   ├── Conv2d_6 (256→256, 3×3)
│   ├── BatchNorm_6
│   ├── Activation_6 (ReLU)
│   └── MaxPool_3 (2×2)
├── Flatten
├── FC_1 (256→512)
├── Activation_7 (ReLU)
├── Dropout (p=0.5)
├── FC_2 (512→256)
├── Activation_8 (ReLU)
└── Head: Linear (256→num_classes) + Softmax
```

### 3.2 Layer-by-Layer Breakdown

#### Block 1 — Feature Extraction (Low-Level)

| Layer | Type | What It Does | Key Params |
|-------|------|-------------|------------|
| `conv1` | Conv2d | Applies 64 filters of size 3×3 to the 3-channel RGB input. Detects edges and simple textures. | in=3, out=64, k=3, pad=1 |
| `bn1` | BatchNorm | Normalizes the 64 feature maps across the batch. Stabilizes training. | features=64 |
| `act1` | ReLU | Applies max(0, x) element-wise. Introduces non-linearity. | — |
| `conv2` | Conv2d | Applies 64 more 3×3 filters. Combines low-level features into slightly more complex patterns. | in=64, out=64, k=3, pad=1 |
| `bn2` | BatchNorm | Normalizes again before the next activation. | features=64 |
| `act2` | ReLU | Non-linearity. | — |
| `pool1` | MaxPool | Halves spatial dimensions (2×2, stride 2). Reduces computation, adds translation invariance. | k=2, s=2 |

#### Block 2 — Feature Extraction (Mid-Level)

| Layer | Type | What It Does | Key Params |
|-------|------|-------------|------------|
| `conv3` | Conv2d | Doubles channels to 128. Detects more complex patterns (corners, textures). | in=64, out=128, k=3, pad=1 |
| `bn3` | BatchNorm | Stabilizes. | features=128 |
| `act3` | ReLU | Non-linearity. | — |
| `conv4` | Conv2d | Refines 128-channel features. | in=128, out=128, k=3, pad=1 |
| `bn4` | BatchNorm | Stabilizes. | features=128 |
| `act4` | ReLU | Non-linearity. | — |
| `pool2` | MaxPool | Halves spatial dimensions again. | k=2, s=2 |

#### Block 3 — Feature Extraction (High-Level)

| Layer | Type | What It Does | Key Params |
|-------|------|-------------|------------|
| `conv5` | Conv2d | Doubles channels to 256. Detects object parts and complex structures. | in=128, out=256, k=3, pad=1 |
| `bn5` | BatchNorm | Stabilizes. | features=256 |
| `act5` | ReLU | Non-linearity. | — |
| `conv6` | Conv2d | Refines 256-channel features. | in=256, out=256, k=3, pad=1 |
| `bn6` | BatchNorm | Stabilizes. | features=256 |
| `act6` | ReLU | Non-linearity. | — |
| `pool3` | MaxPool | Final spatial reduction. | k=2, s=2 |

#### Classification Head

| Layer | Type | What It Does | Key Params |
|-------|------|-------------|------------|
| `flatten` | Flatten | Reshapes 3D feature maps to 1D vector for the FC layers. | — |
| `fc1` | Linear | First fully connected layer. Projects 256 features to 512. | in=256, out=512 |
| `act7` | ReLU | Non-linearity. | — |
| `dropout` | Dropout | Randomly zeros 50% of neurons during training. Prevents overfitting. | p=0.5 |
| `fc2` | Linear | Second FC layer. Compresses 512 to 256 features. | in=512, out=256 |
| `act8` | ReLU | Non-linearity. | — |
| `head` | Linear+Softmax | Final classification. Outputs probability for each class. | in=256, out=num_classes |

#### Channel Progression Pattern

The CNN v16 follows the standard **double-after-pool** pattern:

```
3 → 64 → 64 → [pool] → 128 → 128 → [pool] → 256 → 256 → [pool]
```

This is the VGG-style design: double the channels each time you halve the spatial dimensions, keeping the total "volume" (channels × height × width) roughly constant.

### 3.3 Extensions Reference

The CNN v16 includes **7 extensions** with a total of **30 options**.

#### 1. Optimizer (⚡ training, green) — 4 options

| Option | Code | Default? | Best For |
|--------|------|----------|----------|
| SGD | `optim.SGD(params, lr={lr}, momentum=0.9)` | — | When you have a learning rate schedule |
| Adam | `optim.Adam(params, lr={lr})` | — | Quick experiments, fast convergence |
| **AdamW** | `optim.AdamW(params, lr={lr}, weight_decay=0.01)` | ✅ | Default for most modern architectures |
| RMSprop | `optim.RMSprop(params, lr={lr})` | — | RNNs, rarely for CNNs |

#### 2. Activation Function (🔥 training, green) — 5 options

| Option | Code | Default? | Best For |
|--------|------|----------|----------|
| ReLU | `nn.ReLU(inplace=True)` | — | General default, fast |
| LeakyReLU | `nn.LeakyReLU(0.01, inplace=True)` | — | When you observe dead neurons |
| SiLU (Swish) | `nn.SiLU(inplace=True)` | — | Modern architectures (EfficientNet) |
| Mish | `nn.Mish(inplace=True)` | — | YOLO and similar architectures |
| GELU | `nn.GELU()` | — | Transformers, fine-tuning pretrained models |

*Note: No default is set because the model already uses ReLU internally. This extension lets users override the activation across the network.*

#### 3. Loss Function (💚 training, green) — 3 options

| Option | Code | Default? | Best For |
|--------|------|----------|----------|
| **Cross-Entropy** | `nn.CrossEntropyLoss()` | ✅ | Standard multi-class classification |
| Focal Loss | `FocalLoss(gamma=2.0, alpha=0.25)` | — | Imbalanced datasets |
| Label Smoothing | `nn.CrossEntropyLoss(label_smoothing=0.1)` | — | Preventing overconfident predictions |

#### 4. Learning Rate (📈 training, green) — 4 options

| Option | Value | Default? | Best For |
|--------|-------|----------|----------|
| 0.1 | High | — | SGD with warmup |
| 0.01 | Medium | — | Training from scratch with SGD |
| **0.001** | Low | ✅ | Adam/AdamW default |
| 0.0001 | Very low | — | Fine-tuning pretrained models |

#### 5. Batch Size (📦 functional, yellow) — 5 options

| Option | Value | Default? | GPU Memory |
|--------|-------|----------|------------|
| 8 | Small | — | 2-4 GB |
| **16** | Medium | ✅ | 4-8 GB |
| 32 | Large | — | 8+ GB |
| 64 | Very large | — | 12+ GB |
| 128 | Huge | — | Multi-GPU |

#### 6. Epochs (🔄 functional, yellow) — 4 options

| Option | Value | Default? | Best For |
|--------|-------|----------|----------|
| 50 | Quick | — | Debugging, testing pipeline |
| **100** | Standard | ✅ | Small-medium datasets |
| 200 | Long | — | Medium-large datasets |
| 500 | Very long | — | Maximum performance with early stopping |

#### 7. Data Augmentation (🟣 data, purple) — 4 options

| Option | Transforms | Default? | Best For |
|--------|-----------|----------|----------|
| None | ToTensor + Normalize only | — | Large diverse datasets |
| **Basic** | RandomFlip + Rotation(10°) | ✅ | General-purpose, small datasets |
| Advanced | Flip + Rotation + ColorJitter + RandomCrop | — | Medium datasets needing robustness |
| Custom | User-defined pipeline | — | Domain-specific requirements |

### 3.4 Educational Content in CNN v16

The CNN v16 model includes educational content at two levels:

**Layer-level:** Each layer has an implicit educational explanation served through the `/api/educational/{topic}` endpoint. The topic key is the layer type (e.g., `conv2d`, `batchnorm`, `activation`).

**Extension-level:** Each extension option has inline educational fields:
- `description` — What it is
- `when_to_use` — Practical guidance
- `consequences` — Trade-offs and risks

**Head-level:** The head has a `description` field explaining what the classification head does.

---

## 4. Educational Content Guide

Educational content in NeuroScope serves users who are learning deep learning. It must be accurate, accessible, and practical.

### 4.1 Layer Descriptions (via `/api/educational/{topic}`)

Each topic in `educational.py` has this structure:

```python
"conv2d": {
    "title": "Convolutional Layers (Conv2d)",
    "summary": "One-sentence description of what the layer does.",
    "content": "## Markdown-formatted detailed explanation...",
    "tips": [
        "Practical tip 1",
        "Practical tip 2",
        "Practical tip 3",
    ],
}
```

#### What to Include in `content`

1. **How it works** — Explain the mechanism in plain language. Use analogies when helpful.
2. **Key parameters** — List the most important parameters and what they control.
3. **Why it matters** — Connect the layer to the bigger picture of training a neural network.
4. **Common patterns** — Show how this layer is typically used (e.g., "Conv → BN → ReLU").

#### What to Include in `tips`

- 3-5 actionable tips
- Start with the most important ("Use 3×3 kernels")
- Include common mistakes to avoid
- Keep each tip to one sentence

#### Writing Style

- **Audience:** Beginner to intermediate DL practitioners
- **Tone:** Friendly, direct, no jargon without explanation
- **Length:** Summary = 1 sentence. Content = 200-400 words. Tips = 3-5 items.

#### Example: Good vs. Bad

**Bad:**
> "Conv2d applies a learnable kernel to the input tensor producing an output feature map via cross-correlation."

**Good:**
> "A convolution slides a small filter (kernel) across the input image, computing dot products at each position. This produces a feature map that highlights where specific patterns occur."

### 4.2 Extension Option Content

Each extension option in the model JSON has three educational fields:

#### `description` — What It Is

```
"Adaptive Moment Estimation — adjusts learning rate individually for each parameter
based on first and second moments of gradients."
```

**Rules:**
- 1-2 sentences
- Start with the full name, then explain in plain language
- Mention the key mechanism (what makes it different)

#### `when_to_use` — When to Choose It

```
"Good default for most tasks. Works well without much learning rate tuning."
```

**Rules:**
- 1-2 sentences
- Be specific about scenarios (don't just say "use it when appropriate")
- Mention if it's a default/recommended choice

#### `consequences` — Trade-offs and Risks

```
"Can overfit on small datasets. Weight decay is not properly decoupled from gradient updates."
```

**Rules:**
- 1-2 sentences
- Always mention at least one downside or caveat
- Be honest about limitations
- Don't be alarmist — frame as trade-offs, not warnings

### 4.3 Adding a New Educational Topic

To add a new topic to `educational.py`:

1. **Choose the key:** Use the layer type as the key (e.g., `"lstm"`, `"attention"`, `"globalavgpool"`).

2. **Write the entry:**

```python
"attention": {
    "title": "Attention Mechanisms",
    "summary": "Attention lets the model focus on the most relevant parts of the input when producing each part of the output.",
    "content": (
        "## Attention Mechanisms\n\n"
        "Instead of processing all input equally, attention computes a weighted sum "
        "where the weights are learned based on relevance.\n\n"
        "### Self-Attention\n"
        "Each position attends to all other positions. Used in Transformers.\n\n"
        "### Multi-Head Attention\n"
        "Multiple attention heads capture different types of relationships.\n\n"
        "### Key Parameters\n"
        "- **embed_dim**: Dimension of the input embeddings\n"
        "- **num_heads**: Number of attention heads\n"
        "- **dropout**: Attention weight dropout"
    ),
    "tips": [
        "Use 8 or 16 heads for most tasks",
        "Embedding dimension should be divisible by number of heads",
        "Add positional encoding for sequence data",
    ],
},
```

3. **Test the endpoint:** Verify `GET /api/educational/attention` returns the content correctly.

4. **Update the route docstring** to include the new topic in the available topics list.

### 4.4 Content for Future Model Families

When adding new model families, you may need new educational topics:

| Model Family | New Topics Needed |
|-------------|-------------------|
| YOLO | `anchor_boxes`, `non_max_suppression`, `detection_head`, `iou_loss` |
| ResNet | `skip_connections` (already exists), `residual_block`, `bottleneck` |
| EfficientNet | `compound_scaling`, `squeeze_excitation`, `mbconv` |
| Classical ML | `decision_tree`, `random_foreset`, `svm`, `knn` |

---

## 5. Builder Rules Guide

Builder rules in `config/builder_rules.yaml` validate the user's architecture in real-time and provide feedback.

### 5.1 Rule Structure

Rules are organized into three categories:

```yaml
layer_rules:        # Triggered by individual layer choices
architecture_rules: # Triggered by overall model structure
training_rules:     # Triggered by extension choices
```

### 5.2 Rule Format

Each rule follows this structure:

```yaml
rule_name:
  enabled: true                    # Can be toggled on/off
  severity: WARNING                # ERROR, WARNING, or INFO
  # ... trigger conditions ...
  message: "Human-readable message to display."
```

### 5.3 Severity Levels

| Severity | When to Use | UI Behavior |
|----------|-------------|-------------|
| **ERROR** | The configuration will not work at all. The user *must* fix it. | Red highlight, blocks code generation |
| **WARNING** | The configuration will work but will likely produce poor results. Strong recommendation to change. | Yellow highlight, shows warning icon |
| **INFO** | The configuration is suboptimal or a common beginner mistake. Suggestion, not a requirement. | Blue highlight, shows info icon |

#### Choosing the Right Severity

**ERROR examples:**
- Using Sigmoid output with CrossEntropyLoss (mathematically incorrect)
- Input channels mismatch between consecutive layers
- Output size doesn't match number of classes

**WARNING examples:**
- Sigmoid in deep networks (vanishing gradients)
- Missing BatchNorm in deep CNNs
- Very high learning rate (>0.01)

**INFO examples:**
- No data augmentation (increases overfitting risk)
- Flattening early (loses spatial information)
- Using many FC layers (parameters could be reduced)

### 5.4 Trigger Conditions

#### Layer-Level Triggers

```yaml
# Triggered by layer type
sigmoid_in_deep_network:
  enabled: true
  severity: WARNING
  min_depth: 5              # Only trigger if network has 5+ layers
  message: "Sigmoid activation in a deep network can cause vanishing gradients."

# Triggered by parameter value
large_kernel:
  enabled: true
  severity: WARNING
  max_kernel_size: 7        # Trigger if kernel_size > 7
  message: "Large kernels (>7) are rarely needed."

# Triggered by layer count
missing_batchnorm:
  enabled: true
  severity: WARNING
  min_conv_layers: 5        # Trigger if 5+ conv layers without BatchNorm
  message: "Consider adding BatchNorm after convolutional layers."
```

#### Architecture-Level Triggers

```yaml
# Triggered by overall structure
missing_skip_connections:
  enabled: true
  severity: WARNING
  min_depth: 10             # Trigger if 10+ total layers
  message: "Deep networks (10+ layers) benefit from skip connections."

# Triggered by layer type counts
too_many_fc_layers:
  enabled: true
  severity: WARNING
  max_fc_layers: 3          # Trigger if more than 3 FC layers
  message: "Many FC layers add parameters."
```

#### Training-Level Triggers

```yaml
# Triggered by extension value
high_learning_rate:
  enabled: true
  severity: WARNING
  threshold: 0.01           # Trigger if LR > 0.01
  message: "High learning rate (>0.01) can cause unstable training."

# Triggered by combination of choices
sigmoid_loss_with_deep_network:
  enabled: true
  severity: WARNING
  message: "Using Sigmoid output with CrossEntropyLoss is incorrect."
```

### 5.5 Message Writing Guidelines

**DO:**
- State the problem clearly ("Sigmoid in a deep network...")
- Explain *why* it's a problem ("...can cause vanishing gradients")
- Suggest an alternative ("Consider ReLU or SiLU")
- Keep it to 1-2 sentences

**DON'T:**
- Use jargon without explanation
- Be vague ("This might not be optimal")
- Be condescending ("You clearly don't understand...")
- Write paragraphs — users scan, they don't read

**Template:**
```
{Problem statement}. {Why it matters}. {Suggested alternative}.
```

**Examples:**

```yaml
# Good
message: "Large kernels (>7) are rarely needed. Use stacked 3×3 convolutions instead."

# Good
message: "High learning rate (>0.01) can cause unstable training. Consider warmup or a lower rate."

# Bad — too vague
message: "This might cause issues."

# Bad — too technical
message: "The vanishing gradient problem arises from the saturation regions of the sigmoid function where gradients approach zero."
```

### 5.6 Adding a New Rule

1. **Choose the category:** `layer_rules`, `architecture_rules`, or `training_rules`.

2. **Define the rule:**

```yaml
layer_rules:
  my_new_rule:
    enabled: true
    severity: WARNING
    min_depth: 8
    message: "Clear, actionable message about the problem and solution."
```

3. **Test edge cases:**
   - Does it trigger when it should?
   - Does it *not* trigger when it shouldn't?
   - Is the severity appropriate?

4. **Document** the rule in this guide's trigger conditions table.

---

## 6. Adding a New Model

Step-by-step guide for adding a new model family to NeuroScope.

### 6.1 Pre-Requisites

Before writing any code:

1. **Research the architecture.** Understand the paper, the layer structure, and the key design decisions.
2. **Identify unique layer types.** Does this model use layers not already in `layer_shapes.yaml`?
3. **Plan extensions.** What training hyperparameters matter for this model family?
4. **Check educational content.** Do all layer types used by this model have educational topics?

### 6.2 Step-by-Step

#### Step 1: Create the Model JSON File

```bash
# File: src/data/models/{family}_{version}.json
# Example: src/data/models/yolo_v8.json
```

Follow the schema in [Section 2](#2-model-definition-format). Fill every field.

**Checklist:**
- [ ] `id` is unique and follows snake_case convention
- [ ] `family` groups related models (e.g., all YOLO variants share `family: "YOLO"`)
- [ ] `description` is 1-2 sentences, explains purpose
- [ ] Every layer has `id`, `type`, `name`, `params`, `code`, `freezable`
- [ ] `code` fields are valid PyTorch (copy-pasteable)
- [ ] `head` includes `activation`, `output_neurons`, `description`
- [ ] Every extension has exactly one option with `default: true`
- [ ] Every option has `description`, `when_to_use`, `consequences`

#### Step 2: Add New Layer Types (if needed)

If the model uses layer types not in `layer_shapes.yaml`:

```yaml
# In config/layer_shapes.yaml, add to core_blocks:
new_layer_type:
  geometry: box          # Choose appropriate geometry
  color: "#6366f1"       # Choose a distinct color
  scale_by: output_channels  # What determines size
  label: "ShortLabel"    # 3-5 chars for the 3D block
```

**Geometry options:** `box`, `plane`, `small_cube`, `sphere`, `slab`, `cone`, `wireframe`, `cylinder`, `octahedron`, `merge`, `cube`

#### Step 3: Add Builder Rules (if needed)

If the architecture has common pitfalls:

```yaml
# In config/builder_rules.yaml
architecture_rules:
  yolo_without_spp:
    enabled: true
    severity: WARNING
    message: "YOLO architectures benefit from SPP (Spatial Pyramid Pooling) for multi-scale detection."
```

#### Step 4: Add Educational Content (if needed)

If the model introduces new concepts:

```python
# In src/api/route/educational.py
"anchor_boxes": {
    "title": "Anchor Boxes",
    "summary": "Pre-defined bounding box templates that the model adjusts during prediction.",
    "content": "...",
    "tips": ["..."],
},
```

#### Step 5: Validate

1. **JSON validation:** The model JSON must parse without errors.
2. **PyTorch validation:** Every `code` field must be valid PyTorch when executed.
3. **3D rendering:** Load the model in the builder and verify all layers render correctly.
4. **Builder rules:** Verify rules trigger correctly for common configurations.
5. **Educational content:** Verify all referenced topics exist and are accessible via the API.

### 6.3 Example: Adding ResNet

```json
{
  "id": "resnet_v50",
  "name": "ResNet-50",
  "family": "ResNet",
  "version": "50",
  "description": "50-layer residual network with skip connections. Uses bottleneck blocks for efficient deep learning.",
  "sizes": {
    "18": { "blocks": [2, 2, 2, 2], "description": "18 layers — lightweight" },
    "34": { "blocks": [3, 4, 6, 3], "description": "34 layers — balanced" },
    "50": { "blocks": [3, 4, 6, 3], "description": "50 layers — standard" },
    "101": { "blocks": [3, 4, 23, 3], "description": "101 layers — deep" },
    "152": { "blocks": [3, 8, 36, 3], "description": "152 layers — very deep" }
  },
  "layers": [
    {
      "id": "conv1",
      "type": "conv2d",
      "name": "Conv2d_Stem",
      "params": { "in_channels": 3, "out_channels": 64, "kernel_size": 7, "stride": 2, "padding": 3 },
      "code": "nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3)",
      "freezable": true
    },
    {
      "id": "bn1",
      "type": "batchnorm",
      "name": "BatchNorm_Stem",
      "params": { "num_features": 64 },
      "code": "nn.BatchNorm2d(64)",
      "freezable": true
    },
    {
      "id": "act1",
      "type": "activation",
      "name": "Activation_Stem",
      "params": { "function": "ReLU" },
      "code": "nn.ReLU(inplace=True)",
      "freezable": false
    },
    {
      "id": "pool1",
      "type": "maxpool",
      "name": "MaxPool_Stem",
      "params": { "kernel_size": 3, "stride": 2, "padding": 1 },
      "code": "nn.MaxPool2d(kernel_size=3, stride=2, padding=1)",
      "freezable": false
    }
    // ... residual blocks follow ...
  ],
  "head": {
    "id": "head",
    "type": "linear",
    "name": "Classification Head",
    "activation": "softmax",
    "output_neurons": "num_classes",
    "code": "nn.Linear(2048, num_classes)",
    "activation_code": "nn.Softmax(dim=1)",
    "description": "Global average pooling followed by a single linear layer. The 2048 input features come from the final bottleneck block.",
    "freezable": false
  },
  "extensions": [
    // Same extensions as CNN v16, plus:
    {
      "id": "pretrained",
      "name": "Pretrained Weights",
      "category": "training",
      "color": "green",
      "icon": "🏗️",
      "options": [
        {
          "id": "imagenet",
          "name": "ImageNet",
          "code": "model = torchvision.models.resnet50(weights='IMAGENET1K_V2')",
          "description": "Pretrained on ImageNet (1.2M images, 1000 classes). Features learned for general image recognition.",
          "when_to_use": "Default choice. Transfer learning from ImageNet almost always helps.",
          "consequences": "First few layers learn generic features (edges, textures). Fine-tune only the last few layers for best results.",
          "default": true
        },
        {
          "id": "none",
          "name": "Random",
          "code": "model = torchvision.models.resnet50(weights=None)",
          "description": "Random initialization. Train from scratch.",
          "when_to_use": "When your domain is very different from natural images (e.g., spectrograms, medical scans with unusual modalities).",
          "consequences": "Requires more data and longer training. May not converge to good performance on small datasets.",
          "default": false
        }
      ]
    }
  ]
}
```

### 6.4 Model Family Roadmap

| Priority | Family | Version | Status | Notes |
|----------|--------|---------|--------|-------|
| 1 | ResNet | 50 | Planned | High demand, widely used |
| 2 | YOLO | v8 | Planned | Object detection, needs detection head format |
| 3 | EfficientNet | B0 | Planned | Compound scaling, Squeeze-and-Excitation |
| 4 | Classical ML | — | Future | Decision Tree, Random Forest, SVM, KNN |
| 5 | Transformer | ViT | Future | Vision Transformer, needs patch embedding |

---

## 7. Content Quality Standards

All content produced by the Data Science track must meet these standards.

### 7.1 Language Level

- **Target audience:** Beginner to intermediate DL practitioners (students, junior engineers, self-learners)
- **Reading level:** High school to early college. Avoid graduate-level jargon.
- **Language:** English. Simple sentence structure. Active voice preferred.

### 7.2 Accuracy Requirements

| Content Type | Accuracy Standard |
|-------------|-------------------|
| Layer descriptions | Must match PyTorch documentation. No simplifications that are technically wrong. |
| Code snippets | Must be valid, runnable PyTorch code. Test every snippet. |
| Parameter explanations | Must match actual PyTorch constructor parameters. |
| Educational topics | Must be reviewed against current literature. Cite papers when making specific claims. |
| Builder rules | Must be technically correct. False positives erode user trust. |

### 7.3 Review Process

1. **Self-review:** Author reviews their own content against this guide's standards.
2. **Peer review:** At least one other Data Science team member reviews.
3. **Technical review:** Verify all code snippets run without errors.
4. **UX review:** Verify content is accessible to the target audience.

### 7.4 Content Maintenance

- **When PyTorch updates:** Review all `code` fields for deprecations.
- **When new research emerges:** Update educational topics with current best practices.
- **When users report issues:** Prioritize fixes to incorrect content (highest severity).
- **Quarterly review:** Audit all content for accuracy and relevance.

### 7.5 Checklist for New Content

Before merging any content:

- [ ] All code snippets are valid PyTorch
- [ ] All descriptions use plain language (no unexplained jargon)
- [ ] Every `when_to_use` is specific (not "use when appropriate")
- [ ] Every `consequences` mentions at least one real trade-off
- [ ] Spelling and grammar are correct
- [ ] No hardcoded values that should be parameters
- [ ] Educational topics have 3-5 tips
- [ ] Builder rules use correct severity level
- [ ] JSON is valid and parses without errors
- [ ] Content has been peer-reviewed

---

## Appendix A: File Reference

| File | Purpose | Owner |
|------|---------|-------|
| `src/data/models/*.json` | Model architecture definitions | Data Science |
| `src/api/routes/educational.py` | Educational content API | Data Science |
| `config/builder_rules.yaml` | Builder validation rules | Data Science |
| `config/layer_shapes.yaml` | 3D rendering mappings | Data Science + 3D |

## Appendix B: Common Patterns

### Conv Block Pattern (CNN v16 style)
```
Conv2d → BatchNorm → ReLU → Conv2d → BatchNorm → ReLU → MaxPool
```

### Residual Block Pattern (ResNet style)
```
input → Conv → BN → ReLU → Conv → BN → (+input) → ReLU
```

### Classification Head Pattern
```
GlobalAveragePool → Linear → Softmax
```
or
```
Flatten → Linear → ReLU → Dropout → Linear → Softmax
```

## Appendix C: Extension Categories

| Category | Color | Icon Prefix | Purpose |
|----------|-------|-------------|---------|
| `training` | Green (🟢) | ⚡🔥💚📈 | Hyperparameters that affect training dynamics |
| `functional` | Yellow (🟡) | 📦🔄 | Configuration that affects model behavior |
| `data` | Purple (🟣) | 🟣 | Data preprocessing and augmentation |
