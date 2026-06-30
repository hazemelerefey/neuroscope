# NeuroScope API Reference

> **Version:** 0.2.0  
> **Base URL:** `http://localhost:8000/api`  
> **Framework:** FastAPI  
> **Interactive Docs:** `http://localhost:8000/docs` (Swagger UI) / `http://localhost:8000/redoc` (ReDoc)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Endpoints](#2-endpoints)
   - [Root & Health](#21-root--health)
   - [Models](#22-models)
   - [Export](#23-export)
   - [Educational](#24-educational)
3. [Data Models (Pydantic Schemas)](#3-data-models-pydantic-schemas)
4. [Model Definition Format](#4-model-definition-format)
5. [Builder Rules](#5-builder-rules)
6. [Error Codes](#6-error-codes)
7. [Rate Limiting](#7-rate-limiting)
8. [CORS Configuration](#8-cors-configuration)

---

## 1. Overview

### Authentication

No authentication is currently required. All endpoints are publicly accessible.

### Content Types

| Direction | Content-Type |
|-----------|-------------|
| Request body | `application/json` |
| JSON responses | `application/json` |
| Notebook export | `application/x-ipynb+json` (file download) |
| YAML export | `application/x-yaml` (file download) |

### API Prefix

All API routes are served under the `/api` prefix. The root URL (`/`) and health check (`/health`) are the only exceptions.

---

## 2. Endpoints

### 2.1 Root & Health

#### `GET /`

Returns basic API metadata.

**Response** `200 OK`

```json
{
  "name": "NeuroScope API",
  "version": "0.2.0",
  "description": "Visual Deep Learning Builder",
  "docs": "/docs"
}
```

---

#### `GET /health`

Health check endpoint for monitoring and load balancers.

**Response** `200 OK`

```json
{
  "status": "healthy"
}
```

---

### 2.2 Models

#### `GET /api/models`

List all available model families and their versions. Models are grouped by family name.

**Rate Limit:** 60 requests/minute

**Response** `200 OK`

```json
{
  "families": [
    {
      "family": "CNN",
      "name": "CNN",
      "description": "16-layer Convolutional Neural Network for image classification. A standard architecture with convolutional blocks, batch normalization, and a classification head.",
      "versions": ["16"]
    }
  ],
  "total_models": 1
}
```

**curl Example**

```bash
curl http://localhost:8000/api/models
```

---

#### `GET /api/models/{family}/{version}`

Retrieve the full model definition for a specific architecture family and version. Returns the complete JSON structure including all layers, extensions, options, code snippets, and educational metadata.

**Rate Limit:** 60 requests/minute

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `family` | `string` | Model family name (case-insensitive), e.g., `CNN` |
| `version` | `string` | Model version string, e.g., `16` |

**Response** `200 OK`

Returns the full model definition JSON. See [Model Definition Format](#4-model-definition-format) for the complete schema.

```json
{
  "id": "cnn_v16",
  "name": "CNN v16",
  "family": "CNN",
  "version": "16",
  "description": "16-layer Convolutional Neural Network for image classification...",
  "sizes": null,
  "layers": [ ... ],
  "head": { ... },
  "extensions": [ ... ]
}
```

**Error Responses**

| Status | Condition | Example Detail |
|--------|-----------|----------------|
| `404` | Model not found | `"Model not found: resnet v50. Use GET /api/models to list available models."` |

**curl Example**

```bash
curl http://localhost:8000/api/models/CNN/16
```

---

### 2.3 Export

#### `POST /api/export/notebook`

Generate a downloadable Jupyter notebook (`.ipynb`) from a visual builder configuration. The notebook includes import statements, a PyTorch model class, extension code (optimizer, loss, etc.), and a training loop.

**Rate Limit:** 20 requests/minute

**Request Body** — `application/json`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `model_family` | `string` | ✅ | — | Model family name (e.g., `"CNN"`) |
| `model_version` | `string` | ✅ | — | Model version (e.g., `"16"`) |
| `model_name` | `string` | ❌ | `"MyModel"` | Name for the generated model class |
| `layers` | [`LayerConfig[]`](#layerconfig) | ✅ | — | Ordered list of layers in the model |
| `extensions` | [`ExtensionChoice[]`](#extensionchoice) | ✅ | — | User-selected extension options |
| `num_classes` | `integer` | ❌ | `10` | Number of output classes |
| `input_shape` | `integer[]` | ❌ | `[3, 224, 224]` | Input tensor shape (C, H, W) |

**Response** `200 OK`

Returns a file download. The response is a Jupyter notebook file streamed as `application/x-ipynb+json` with a `Content-Disposition` header suggesting the filename `{model_name}.ipynb`.

**Error Responses**

| Status | Condition | Example Detail |
|--------|-----------|----------------|
| `404` | Model definition not found | `"Model definition not found: CNN v99"` |
| `422` | Validation error | Standard FastAPI validation error body |
| `500` | Missing dependency | `"nbformat is required for notebook generation. Install with: pip install nbformat"` |

**curl Example**

```bash
curl -X POST http://localhost:8000/api/export/notebook \
  -H "Content-Type: application/json" \
  -o MyCNN.ipynb \
  -d '{
    "model_family": "CNN",
    "model_version": "16",
    "model_name": "MyCNN",
    "layers": [
      { "id": "conv1", "type": "conv2d", "name": "Conv2d_1", "params": { "code": "nn.Conv2d(3, 64, kernel_size=3, padding=1)" } },
      { "id": "bn1", "type": "batchnorm", "name": "BatchNorm_1", "params": { "code": "nn.BatchNorm2d(64)" } },
      { "id": "act1", "type": "activation", "name": "Activation_1", "params": { "code": "nn.ReLU(inplace=True)" } }
    ],
    "extensions": [
      { "extension_id": "optimizer", "option_id": "adamw" },
      { "extension_id": "loss", "option_id": "cross_entropy" },
      { "extension_id": "learning_rate", "option_id": "lr_0001" }
    ],
    "num_classes": 10,
    "input_shape": [3, 224, 224]
  }'
```

---

#### `POST /api/export/yaml`

Generate a downloadable YAML model configuration file from a visual builder setup. Produces a structured YAML describing the architecture, layer configs, and training hyperparameters.

**Rate Limit:** 20 requests/minute

**Request Body** — `application/json`

Identical schema to [ExportNotebookRequest](#exportnotebookrequest). See the table above.

**Response** `200 OK`

Returns a file download as `application/x-yaml` with filename `{model_name}_config.yaml`.

**Example YAML Output**

```yaml
model:
  name: MyCNN
  family: CNN
  version: '16'
  num_classes: 10
  input_shape:
  - 3
  - 224
  - 224
layers:
- id: conv1
  type: conv2d
  name: Conv2d_1
  params:
    in_channels: 3
    out_channels: 64
    kernel_size: 3
    padding: 1
- id: bn1
  type: batchnorm
  name: BatchNorm_1
  params:
    num_features: 64
training:
  optimizer:
    choice: AdamW
    code: optimizer = optim.AdamW(model.parameters(), lr={lr}, weight_decay=0.01)
  loss_function:
    choice: Cross-Entropy Loss
    code: criterion = nn.CrossEntropyLoss()
  learning_rate:
    choice: '0.001'
    code: lr0 = 0.001
```

**Error Responses**

Same as [Export Notebook](#post-exportnotebook), plus:

| Status | Condition | Example Detail |
|--------|-----------|----------------|
| `500` | Missing dependency | `"pyyaml is required for YAML export. Install with: pip install pyyaml"` |

**curl Example**

```bash
curl -X POST http://localhost:8000/api/export/yaml \
  -H "Content-Type: application/json" \
  -o MyCNN_config.yaml \
  -d '{
    "model_family": "CNN",
    "model_version": "16",
    "model_name": "MyCNN",
    "layers": [
      { "id": "conv1", "type": "conv2d", "name": "Conv2d_1", "params": {} },
      { "id": "bn1", "type": "batchnorm", "name": "BatchNorm_1", "params": {} }
    ],
    "extensions": [
      { "extension_id": "optimizer", "option_id": "adamw" },
      { "extension_id": "loss", "option_id": "cross_entropy" }
    ],
    "num_classes": 10,
    "input_shape": [3, 224, 224]
  }'
```

---

### 2.4 Educational

#### `GET /api/educational`

List all available educational topics with their titles and summaries.

**Rate Limit:** 60 requests/minute

**Response** `200 OK`

```json
{
  "topics": [
    {
      "id": "conv2d",
      "title": "Convolutional Layers (Conv2d)",
      "summary": "Convolutional layers are the building blocks of CNNs. They apply learnable filters to input feature maps to detect spatial patterns like edges, textures, and shapes."
    },
    {
      "id": "batchnorm",
      "title": "Batch Normalization",
      "summary": "BatchNorm normalizes activations across the batch dimension, stabilizing training and allowing higher learning rates."
    },
    {
      "id": "activation",
      "title": "Activation Functions",
      "summary": "Activation functions introduce non-linearity into neural networks, enabling them to learn complex patterns."
    },
    {
      "id": "pooling",
      "title": "Pooling Layers",
      "summary": "Pooling reduces spatial dimensions, decreasing computation and introducing translation invariance."
    },
    {
      "id": "dropout",
      "title": "Dropout",
      "summary": "Dropout randomly zeros neurons during training, preventing co-adaptation and overfitting."
    },
    {
      "id": "optimizer",
      "title": "Optimizers",
      "summary": "Optimizers update model weights to minimize the loss function. Different algorithms have different trade-offs."
    },
    {
      "id": "loss_function",
      "title": "Loss Functions",
      "summary": "Loss functions measure how far the model's predictions are from the ground truth."
    },
    {
      "id": "data_augmentation",
      "title": "Data Augmentation",
      "summary": "Augmentation artificially increases training data diversity by applying random transformations."
    },
    {
      "id": "skip_connections",
      "title": "Skip Connections",
      "summary": "Skip connections (residual connections) allow gradients to flow directly through the network, enabling training of very deep models."
    },
    {
      "id": "learning_rate",
      "title": "Learning Rate",
      "summary": "The learning rate controls how much weights are updated during training. It's the most important hyperparameter."
    }
  ],
  "total": 10
}
```

**curl Example**

```bash
curl http://localhost:8000/api/educational
```

---

#### `GET /api/educational/{topic}`

Get detailed educational content for a specific deep learning topic. Returns a structured explanation with markdown content, practical tips, and contextual guidance.

**Rate Limit:** 60 requests/minute

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic` | `string` | Topic ID. Hyphens and spaces are auto-converted to underscores. |

**Available Topics**

| Topic ID | Title |
|----------|-------|
| `conv2d` | Convolutional Layers (Conv2d) |
| `batchnorm` | Batch Normalization |
| `activation` | Activation Functions |
| `pooling` | Pooling Layers |
| `dropout` | Dropout |
| `optimizer` | Optimizers |
| `loss_function` | Loss Functions |
| `data_augmentation` | Data Augmentation |
| `skip_connections` | Skip Connections |
| `learning_rate` | Learning Rate |

**Response** `200 OK`

```json
{
  "title": "Convolutional Layers (Conv2d)",
  "summary": "Convolutional layers are the building blocks of CNNs...",
  "content": "## How Conv2d Works\n\nA convolution slides a small filter (kernel) across the input image...",
  "tips": [
    "Start with 3×3 kernels — they're the sweet spot for most tasks",
    "Use padding=1 to preserve spatial dimensions",
    "Double channels after each pooling layer (64 → 128 → 256)"
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `title` | `string` | Human-readable topic title |
| `summary` | `string` | One-paragraph summary |
| `content` | `string` | Full explanation in Markdown format |
| `tips` | `string[]` | Practical tips and best practices |

**Error Responses**

| Status | Condition | Example Detail |
|--------|-----------|----------------|
| `404` | Topic not found | `"Topic 'transformer' not found. Available topics: activation, batchnorm, conv2d, ..."` |

**curl Examples**

```bash
# Fetch educational content for conv2d
curl http://localhost:8000/api/educational/conv2d

# Hyphens are auto-converted — these are equivalent:
curl http://localhost:8000/api/educational/loss-function
curl http://localhost:8000/api/educational/loss_function
```

---

## 3. Data Models (Pydantic Schemas)

### `LayerConfig`

A single layer in the user's visual model configuration. Used in export requests.

```json
{
  "id": "conv1",
  "type": "conv2d",
  "name": "Conv2d_1",
  "params": {
    "code": "nn.Conv2d(3, 64, kernel_size=3, padding=1)",
    "in_channels": 3,
    "out_channels": 64,
    "kernel_size": 3,
    "padding": 1
  }
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | `string` | ✅ | — | Unique layer identifier |
| `type` | `string` | ✅ | — | Layer type (e.g., `conv2d`, `batchnorm`, `activation`, `maxpool`, `flatten`, `linear`, `dropout`) |
| `name` | `string` | ✅ | — | Display name for the layer |
| `params` | `object` | ❌ | `{}` | Layer parameters. May include a `code` key with the PyTorch code snippet |

---

### `ExtensionChoice`

User's selection for a single extension (optimizer, loss function, etc.).

```json
{
  "extension_id": "optimizer",
  "option_id": "adamw"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `extension_id` | `string` | ✅ | Extension category ID (e.g., `optimizer`, `loss`, `learning_rate`, `batch_size`, `epochs`, `augmentation`, `activation`) |
| `option_id` | `string` | ✅ | Selected option ID within the extension (e.g., `adamw`, `cross_entropy`, `lr_0001`) |

---

### `ExportNotebookRequest`

Full request schema for Jupyter notebook generation.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `model_family` | `string` | ✅ | — | Architecture family (e.g., `"CNN"`) |
| `model_version` | `string` | ✅ | — | Architecture version (e.g., `"16"`) |
| `model_name` | `string` | ❌ | `"MyModel"` | Name used in the notebook title and generated class |
| `layers` | `LayerConfig[]` | ✅ | — | Ordered list of model layers |
| `extensions` | `ExtensionChoice[]` | ✅ | — | Selected extension options |
| `num_classes` | `integer` | ❌ | `10` | Number of output classes for the classification head |
| `input_shape` | `integer[]` | ❌ | `[3, 224, 224]` | Input tensor dimensions as `[C, H, W]` |

---

### `ExportYamlRequest`

Full request schema for YAML configuration export. Identical fields to `ExportNotebookRequest`.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `model_family` | `string` | ✅ | — | Architecture family |
| `model_version` | `string` | ✅ | — | Architecture version |
| `model_name` | `string` | ❌ | `"MyModel"` | Model name in the YAML header |
| `layers` | `LayerConfig[]` | ✅ | — | Ordered list of model layers |
| `extensions` | `ExtensionChoice[]` | ✅ | — | Selected extension options |
| `num_classes` | `integer` | ❌ | `10` | Number of output classes |
| `input_shape` | `integer[]` | ❌ | `[3, 224, 224]` | Input tensor dimensions |

---

### `ModelFamily` (Response Schema)

Returned by `GET /api/models`.

| Field | Type | Description |
|-------|------|-------------|
| `family` | `string` | Family identifier |
| `name` | `string` | Display name |
| `description` | `string` | Family description |
| `versions` | `string[]` | Available version strings |

---

### `ModelDefinition` (Response Schema)

Returned by `GET /api/models/{family}/{version}`.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique model ID (e.g., `"cnn_v16"`) |
| `name` | `string` | Display name (e.g., `"CNN v16"`) |
| `family` | `string` | Family identifier |
| `version` | `string` | Version string |
| `description` | `string` | Architecture description |
| `sizes` | `object \| null` | Size variants (if applicable) |
| `layers` | `LayerDefinition[]` | Full layer definitions with code |
| `head` | `object` | Classification head definition |
| `extensions` | `Extension[]` | Available extensions and options |

---

### `LayerDefinition`

A layer as served by the model definition API (richer than `LayerConfig`).

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique layer identifier |
| `type` | `string` | Layer type |
| `name` | `string` | Display name |
| `params` | `object` | Layer parameters |
| `code` | `string` | PyTorch code snippet |
| `freezable` | `boolean` | Whether the layer supports weight freezing for transfer learning |

---

### `Extension`

An extension category as served by the model definition API.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Extension ID (e.g., `"optimizer"`, `"loss"`) |
| `name` | `string` | Display name (e.g., `"Optimizer"`) |
| `category` | `string` | Category: `"training"`, `"functional"`, or `"data"` |
| `color` | `string` | UI color token (e.g., `"green"`, `"yellow"`, `"purple"`) |
| `icon` | `string` | Emoji icon |
| `options` | `ExtensionOption[]` | Available choices |

---

### `ExtensionOption`

A single selectable option within an extension.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Option ID (e.g., `"adamw"`, `"cross_entropy"`) |
| `name` | `string` | Display name (e.g., `"AdamW"`) |
| `code` | `string` | PyTorch code snippet for this option |
| `description` | `string` | What this option does |
| `when_to_use` | `string` | Guidance on when to select this option |
| `consequences` | `string` | Trade-offs and side effects |
| `default` | `boolean` | Whether this is the recommended default |

---

## 4. Model Definition Format

Model definitions are stored as JSON files in `src/data/models/`. Here is the complete structure using CNN v16 as the reference example.

### Top-Level Structure

```json
{
  "id": "cnn_v16",
  "name": "CNN v16",
  "family": "CNN",
  "version": "16",
  "description": "16-layer Convolutional Neural Network for image classification...",
  "sizes": null,
  "layers": [ ... ],
  "head": { ... },
  "extensions": [ ... ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier, matches the filename (e.g., `cnn_v16.json`) |
| `name` | `string` | Human-readable name |
| `family` | `string` | Architecture family for grouping |
| `version` | `string` | Version string |
| `description` | `string` | Architecture description |
| `sizes` | `object \| null` | Size variants (e.g., small/medium/large). `null` if not applicable |
| `layers` | `array` | Ordered list of layer definitions |
| `head` | `object` | Classification head definition |
| `extensions` | `array` | Configurable training/data extensions |

### Layer Object

```json
{
  "id": "conv1",
  "type": "conv2d",
  "name": "Conv2d_1",
  "params": {
    "in_channels": 3,
    "out_channels": 64,
    "kernel_size": 3,
    "padding": 1
  },
  "code": "nn.Conv2d(3, 64, kernel_size=3, padding=1)",
  "freezable": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique layer identifier |
| `type` | `string` | Layer type. Known values: `conv2d`, `batchnorm`, `activation`, `maxpool`, `flatten`, `linear`, `dropout` |
| `name` | `string` | Display name |
| `params` | `object` | Layer-specific parameters (varies by type) |
| `code` | `string` | PyTorch constructor code |
| `freezable` | `boolean` | `true` for layers with learnable weights (Conv, BN, Linear); `false` for activations, pooling, dropout |

### Head Object

```json
{
  "id": "head",
  "type": "linear",
  "name": "Classification Head",
  "activation": "softmax",
  "output_neurons": "num_classes",
  "code": "nn.Linear(256, num_classes)",
  "activation_code": "nn.Softmax(dim=1)",
  "description": "The classification head — outputs probability for each class...",
  "freezable": false
}
```

### CNN v16 Architecture Summary

The CNN v16 model consists of 28 layers organized in three convolutional blocks:

| Block | Layers | Channels | Spatial |
|-------|--------|----------|---------|
| Block 1 | Conv→BN→ReLU→Conv→BN→ReLU→MaxPool | 3→64→64 | 224→112 |
| Block 2 | Conv→BN→ReLU→Conv→BN→ReLU→MaxPool | 64→128→128 | 112→56 |
| Block 3 | Conv→BN→ReLU→Conv→BN→ReLU→MaxPool | 128→256→256 | 56→28 |
| Classifier | Flatten→FC→ReLU→Dropout(0.5)→FC→ReLU | 256→512→256 | — |
| Head | FC(num_classes) + Softmax | 256→N | — |

### Extensions Reference

The CNN v16 model provides 8 configurable extensions:

| Extension | ID | Category | Default Option |
|-----------|----|----------|----------------|
| Optimizer | `optimizer` | training | AdamW |
| Activation Function | `activation` | training | (none set) |
| Loss Function | `loss` | training | Cross-Entropy Loss |
| Learning Rate | `learning_rate` | training | 0.001 |
| Batch Size | `batch_size` | functional | 16 |
| Epochs | `epochs` | functional | 100 |
| Data Augmentation | `augmentation` | data | Basic |

Each extension option provides:
- **code**: PyTorch code snippet (with `{lr}` placeholder for optimizer)
- **description**: What the option does
- **when_to_use**: Selection guidance
- **consequences**: Trade-offs

---

## 5. Builder Rules

The builder validates user configurations against a set of rules defined in `config/builder_rules.yaml`. Rules are categorized by scope and have severity levels.

### Severity Levels

| Level | Meaning |
|-------|---------|
| `INFO` | Suggestion — improves architecture but not critical |
| `WARNING` | Potential problem — should be addressed |

### Layer Rules

Triggered by individual layer choices within the model.

| Rule | Severity | Trigger Condition | Message |
|------|----------|-------------------|---------|
| `sigmoid_in_deep_network` | WARNING | Network depth ≥ 5 and Sigmoid activation used | Sigmoid activation in a deep network can cause vanishing gradients. Consider ReLU or SiLU. |
| `tanh_in_deep_network` | WARNING | Network depth ≥ 5 and Tanh activation used | Tanh activation in a deep network can cause vanishing gradients. Consider ReLU or SiLU. |
| `missing_batchnorm` | WARNING | ≥ 5 Conv layers and no BatchNorm | Consider adding BatchNorm after convolutional layers for training stability. |
| `large_kernel` | WARNING | Kernel size > 7 | Large kernels (>7) are rarely needed. Use stacked 3×3 convolutions instead. |

### Architecture Rules

Triggered by the overall model structure.

| Rule | Severity | Trigger Condition | Message |
|------|----------|-------------------|---------|
| `missing_skip_connections` | WARNING | Network depth ≥ 10, no skip connections | Deep networks (10+ layers) benefit from skip connections to prevent vanishing gradients. |
| `no_pooling` | WARNING | ≥ 3 Conv layers, no pooling | Multiple conv layers without pooling will be computationally expensive. Add MaxPool or stride-2 convolutions. |
| `premature_flatten` | INFO | Flatten used before final conv block | Flattening early loses spatial information. Consider GlobalAveragePool instead. |
| `too_many_fc_layers` | WARNING | > 3 fully connected layers | Many FC layers add parameters. Consider GlobalAveragePool + single FC head. |

### Training Rules

Triggered by extension choices (optimizer, loss, batch size, etc.).

| Rule | Severity | Trigger Condition | Message |
|------|----------|-------------------|---------|
| `high_learning_rate` | WARNING | Learning rate > 0.01 | High learning rate (>0.01) can cause unstable training. Consider warmup or a lower rate. |
| `sigmoid_loss_with_deep_network` | WARNING | Sigmoid output + CrossEntropyLoss | Using Sigmoid output with CrossEntropyLoss is incorrect. CrossEntropyLoss includes LogSoftmax internally. |
| `no_augmentation` | INFO | No augmentation selected | No data augmentation increases overfitting risk, especially on small datasets. |
| `large_batch_small_dataset` | WARNING | Large batch size + small dataset | Large batch size with small dataset may cause overfitting. Consider reducing batch size. |

### Hardware Presets

Used for training time estimation.

| GPU | FP32 TFLOPS | FP16 TFLOPS | Memory (GB) |
|-----|-------------|-------------|-------------|
| T4 | 8.1 | 65 | 16 |
| V100 | 15.7 | 125 | 32 |
| A100 | 19.5 | 312 | 80 |
| RTX 3090 | 35.6 | 71 | 24 |
| RTX 4090 | 82.6 | 165 | 24 |
| CPU | 0.5 | 0.5 | — |

---

## 6. Error Codes

### Standard HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| `200` | OK | Successful request |
| `404` | Not Found | Model family/version not found; educational topic not found |
| `422` | Unprocessable Entity | Request body fails Pydantic validation (wrong types, missing required fields) |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Missing Python dependency (`nbformat`, `pyyaml`); models directory not found |

### Error Response Format

All error responses follow the standard FastAPI format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (422), FastAPI returns a structured body:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "model_family"],
      "msg": "Field required",
      "input": { ... },
      "url": "https://errors.pydantic.dev/2.x/v/missing"
    }
  ]
}
```

### Rate Limit Error

When rate limits are exceeded (429), the response uses the SlowAPI format:

```json
{
  "detail": "Rate limit exceeded: 60/minute"
}
```

---

## 7. Rate Limiting

Rate limiting is enforced via [SlowAPI](https://github.com/laurentS/slowapi) using the client's remote IP address.

| Endpoint Group | Limit | Scope |
|----------------|-------|-------|
| Model listing & retrieval | 60 requests/minute | Per IP |
| Export (notebook & YAML) | 20 requests/minute | Per IP |
| Educational content | 60 requests/minute | Per IP |
| Root & Health | No limit | — |

When the limit is exceeded, the API returns `429 Too Many Requests`.

---

## 8. CORS Configuration

### Development Mode (default)

Allowed origins when `ENVIRONMENT` is not set or set to `"development"`:

| Origin |
|--------|
| `http://localhost:5173` |
| `http://localhost:3000` |
| `http://127.0.0.1:5173` |

### Production Mode

When `ENVIRONMENT=production`, allowed origins are read from the `ALLOWED_ORIGINS` environment variable (comma-separated). Defaults to `http://localhost:3000`.

```
ALLOWED_ORIGINS=https://app.neuroscope.ai,https://staging.neuroscope.ai
```

### CORS Settings

| Setting | Value |
|---------|-------|
| `allow_credentials` | `true` |
| `allow_methods` | `*` (all HTTP methods) |
| `allow_headers` | `*` (all headers) |

---

## Appendix: Quick Reference

### All Endpoints at a Glance

| Method | URL | Description | Rate Limit |
|--------|-----|-------------|------------|
| `GET` | `/` | API metadata | — |
| `GET` | `/health` | Health check | — |
| `GET` | `/api/models` | List model families | 60/min |
| `GET` | `/api/models/{family}/{version}` | Get model definition | 60/min |
| `POST` | `/api/export/notebook` | Generate Jupyter notebook | 20/min |
| `POST` | `/api/export/yaml` | Generate YAML config | 20/min |
| `GET` | `/api/educational` | List educational topics | 60/min |
| `GET` | `/api/educational/{topic}` | Get topic content | 60/min |

### Extension Option IDs Reference

For use with the export endpoints:

**Optimizer** (`optimizer`): `sgd`, `adam`, `adamw`, `rmsprop`  
**Activation** (`activation`): `relu`, `leaky_relu`, `silu`, `mish`, `gelu`  
**Loss Function** (`loss`): `cross_entropy`, `focal_loss`, `label_smoothing`  
**Learning Rate** (`learning_rate`): `lr_01`, `lr_001`, `lr_0001`, `lr_00001`  
**Batch Size** (`batch_size`): `batch_8`, `batch_16`, `batch_32`, `batch_64`, `batch_128`  
**Epochs** (`epochs`): `epochs_50`, `epochs_100`, `epochs_200`, `epochs_500`  
**Data Augmentation** (`augmentation`): `none`, `basic`, `advanced`, `custom`

---

*Generated from NeuroScope backend source — `src/main.py`, `src/api/routes/`, `src/data/models/`, `config/builder_rules.yaml`*
