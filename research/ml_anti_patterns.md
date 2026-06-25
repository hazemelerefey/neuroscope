# ML Architecture Anti-Patterns Catalog

> A comprehensive reference for automated "ML linter" tools.
> Each entry includes: name, description, programmatic detection, severity, fix, and examples.

---

## Table of Contents

1. [Layer-Level Anti-Patterns](#1-layer-level-anti-patterns)
2. [Architecture-Level Anti-Patterns](#2-architecture-level-anti-patterns)
3. [Training-Related Red Flags](#3-training-related-red-flags)
4. [Efficiency Anti-Patterns](#4-efficiency-anti-patterns)
5. [Task-Specific Rules](#5-task-specific-rules)
6. [FLOPs Calculation](#6-calculating-flops-from-layer-parameters)
7. [Memory Footprint Estimation](#7-estimating-model-memory-footprint)
8. [Training Time Estimation](#8-estimating-training-time)
9. [Model Card Standard](#9-model-card-standard-fields)

---

## 1. Layer-Level Anti-Patterns

### 1.1 Missing Activation Function

**Description:** A linear layer (Dense, Conv) is not followed by a non-linear activation. Stacking linear layers without activations collapses to a single linear transformation, making the network unable to learn non-linear decision boundaries.

**Severity:** Critical

**Detection:**
- Traverse the computation graph. For every linear layer (Dense, Conv1d/2d/3d, Linear), check if the output feeds into a non-linear activation (ReLU, GELU, SiLU, Sigmoid, Tanh, etc.) or a loss function before the next linear layer.
- Exception: the final layer before a loss that implicitly includes activation (e.g., `CrossEntropyLoss` includes softmax).

**Suggested Fix:** Insert an appropriate activation after each hidden linear layer.

**Example:**
```python
# ❌ BAD: Two linear layers with no activation between them
model = nn.Sequential(
    nn.Linear(512, 256),
    nn.Linear(256, 10)   # collapses to one linear transform
)

# ✅ GOOD: Activation between linear layers
model = nn.Sequential(
    nn.Linear(512, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)
```

---

### 1.2 Sigmoid/Tanh in Deep Networks (Vanishing Gradient Amplifier)

**Description:** Using sigmoid or tanh activations in networks deeper than ~5 layers. These saturate for large inputs, producing gradients near zero, which compounds across layers and causes vanishing gradients.

**Severity:** Critical

**Detection:**
- Count depth of network. If depth > 5 and any hidden layer uses sigmoid/tanh → flag.
- Exception: sigmoid at final layer for binary classification, tanh when output must be in [-1, 1].

**Suggested Fix:** Replace with ReLU, Leaky ReLU, GELU, SiLU/Swish, or Mish.

**Example:**
```python
# ❌ BAD: Sigmoid in a 10-layer network
for i in range(10):
    layers += [nn.Linear(256, 256), nn.Sigmoid()]

# ✅ GOOD: ReLU (or GELU/SiLU) for hidden layers
for i in range(10):
    layers += [nn.Linear(256, 256), nn.ReLU()]
# Sigmoid only at the end if binary classification
layers += [nn.Linear(256, 1), nn.Sigmoid()]
```

---

### 1.3 ReLU in RNN/LSTM Internal Gates

**Description:** Replacing sigmoid/tanh inside RNN/LSTM gate mechanisms with ReLU. Gates require outputs in bounded ranges to control information flow; ReLU is unbounded and breaks gating semantics.

**Severity:** Critical

**Detection:**
- If layer is LSTM/GRU/RNN cell and custom activation override specifies ReLU → flag.
- Standard framework defaults are safe; only flag explicit overrides.

**Suggested Fix:** Use default sigmoid for gates, tanh for candidate hidden state.

**Example:**
```python
# ❌ BAD
nn.LSTM(input_size=128, hidden_size=256, nonlinearity='relu')

# ✅ GOOD
nn.LSTM(input_size=128, hidden_size=256)  # defaults: sigmoid gates, tanh candidate
```

---

### 1.4 Missing Batch Normalization in Deep CNNs

**Description:** Deep convolutional networks (>8 layers) without batch normalization suffer from internal covariate shift, making training unstable and slower to converge.

**Severity:** Warning

**Detection:**
- Count consecutive Conv layers without intervening BatchNorm. If chain length ≥ 3 → flag.
- Exception: architectures designed without BN (e.g., using GroupNorm, LayerNorm, or weight-standardization).

**Suggested Fix:** Add BatchNorm (or GroupNorm/LayerNorm) after each Conv layer.

**Example:**
```python
# ❌ BAD: Multiple conv layers without normalization
self.block = nn.Sequential(
    nn.Conv2d(64, 64, 3, padding=1),
    nn.ReLU(),
    nn.Conv2d(64, 64, 3, padding=1),
    nn.ReLU(),
    nn.Conv2d(64, 64, 3, padding=1),
    nn.ReLU(),
)

# ✅ GOOD: BatchNorm after each conv
self.block = nn.Sequential(
    nn.Conv2d(64, 64, 3, padding=1),
    nn.BatchNorm2d(64),
    nn.ReLU(),
    nn.Conv2d(64, 64, 3, padding=1),
    nn.BatchNorm2d(64),
    nn.ReLU(),
    nn.Conv2d(64, 64, 3, padding=1),
    nn.BatchNorm2d(64),
    nn.ReLU(),
)
```

---

### 1.5 Batch Normalization Placement Debate (Before vs. After Activation)

**Description:** The ordering of BatchNorm relative to activation is debated. Original paper places BN before activation. Modern practice (ResNet v2, He et al. 2016) places BN before activation. Placing BN after ReLU is problematic because ReLU already clips negative values, wasting BN's bias correction.

**Severity:** Info

**Detection:**
- Detect pattern: `Conv → ReLU → BN` (BN after activation) → flag as suboptimal.
- Preferred: `Conv → BN → ReLU` or `Conv → BN → ReLU` (pre-activation variant: `BN → ReLU → Conv`).

**Suggested Fix:** Use `Conv → BN → Activation` (post-conv normalization) or the pre-activation residual block `BN → ReLU → Conv`.

**Example:**
```python
# ⚠️ SUBOPTIMAL: BN after activation
nn.Sequential(nn.Conv2d(64, 64, 3), nn.ReLU(), nn.BatchNorm2d(64))

# ✅ GOOD: BN before activation (standard)
nn.Sequential(nn.Conv2d(64, 64, 3), nn.BatchNorm2d(64), nn.ReLU())

# ✅ GOOD: Pre-activation residual block (He et al. 2016)
class PreActBlock(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.bn1 = nn.BatchNorm2d(ch)
        self.conv1 = nn.Conv2d(ch, ch, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(ch)
        self.conv2 = nn.Conv2d(ch, ch, 3, padding=1)

    def forward(self, x):
        out = F.relu(self.bn1(x))
        out = self.conv1(out)
        out = self.conv2(F.relu(self.bn2(out)))
        return out + x
```

---

### 1.6 Dropout in Wrong Locations

**Description:** Dropout placed before batch normalization (which negates dropout's effect), or dropout missing entirely in large fully-connected classification heads.

**Severity:** Warning

**Detection:**
- Pattern `Dropout → BN` → flag (BN normalizes the stochastic activations, reducing dropout's regularization effect).
- Large FC layer (output dim > 512) with no dropout → flag.

**Suggested Fix:** Place dropout after activation, before the next linear layer. Use `Dropout → Linear` or `Linear → ReLU → Dropout → Linear`.

**Example:**
```python
# ❌ BAD: Dropout before BN
nn.Sequential(nn.Dropout(0.5), nn.BatchNorm2d(64), nn.ReLU())

# ❌ BAD: Large FC layer with no dropout
nn.Sequential(nn.Linear(4096, 4096), nn.ReLU(), nn.Linear(4096, 1000))

# ✅ GOOD: Dropout after activation, before next linear
nn.Sequential(nn.Linear(4096, 4096), nn.ReLU(), nn.Dropout(0.5), nn.Linear(4096, 1000))
```

---

### 1.7 Incorrect Weight Initialization

**Description:** Using default initialization (often uniform or normal with fixed scale) without considering the activation function. ReLU-family activations require He initialization; sigmoid/tanh require Xavier/Glorot.

**Severity:** Warning

**Detection:**
- If activation is ReLU-family and init is not He (Kaiming) → flag.
- If activation is sigmoid/tanh and init is not Xavier (Glorot) → flag.
- Flag layers using default init when network depth > 10.

**Suggested Fix:**
```python
# For ReLU layers
nn.init.kaiming_normal_(layer.weight, mode='fan_in', nonlinearity='relu')
# For sigmoid/tanh layers
nn.init.xavier_normal_(layer.weight)
```

**Example:**
```python
# ❌ BAD: Default init with deep ReLU network
layer = nn.Linear(512, 512)  # default: uniform(-sqrt(k), sqrt(k))

# ✅ GOOD: He initialization for ReLU
layer = nn.Linear(512, 512)
nn.init.kaiming_normal_(layer.weight, mode='fan_in', nonlinearity='relu')
```

---

### 1.8 Bias with Batch Normalization

**Description:** Using `bias=True` in a Conv/Linear layer that is immediately followed by BatchNorm. BN has its own bias parameter (β), making the layer's bias redundant. The bias is subtracted during BN's mean computation and has no effect.

**Severity:** Info

**Detection:**
- Pattern: `Conv/Linear(bias=True) → BatchNorm` → flag redundant bias.

**Suggested Fix:** Set `bias=False` in the Conv/Linear layer when followed by BN.

**Example:**
```python
# ⚠️ WASTEFUL: bias=True before BN
nn.Conv2d(64, 128, 3, bias=True)  # bias is negated by BN
nn.BatchNorm2d(128)

# ✅ GOOD: bias=False before BN
nn.Conv2d(64, 128, 3, bias=False)
nn.BatchNorm2d(128)
```

---

## 2. Architecture-Level Anti-Patterns

### 2.1 Deep Network Without Skip/Residual Connections

**Description:** Networks deeper than ~20 layers without skip connections suffer from degradation: training accuracy degrades with depth, not due to overfitting but optimization difficulty. Vanishing gradients make early layers untrainable.

**Severity:** Critical

**Detection:**
- If network depth (longest path in layers) > 20 and no skip/residual connections detected → flag.
- Detect skip connections: look for add/concat operations that bypass one or more layers.

**Suggested Fix:** Add residual connections (identity shortcuts) every 2-3 layers.

**Example:**
```python
# ❌ BAD: 30-layer plain network
layers = [nn.Linear(256, 256), nn.ReLU()] * 15  # no shortcuts

# ✅ GOOD: Residual blocks
class ResBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, dim), nn.ReLU(),
            nn.Linear(dim, dim)
        )
    def forward(self, x):
        return F.relu(self.net(x) + x)  # skip connection
```

---

### 2.2 Parameter Explosion in Fully Connected Layers

**Description:** Transitioning from convolutional to fully connected layers by flattening creates enormous parameter counts. E.g., a 7×7×512 feature map flattened to a 4096-unit FC layer = 102M parameters in one layer.

**Severity:** Warning

**Detection:**
- For any Linear layer, compute `in_features × out_features`. If > 50M parameters in a single layer → flag.
- Detect flattening of spatial feature maps followed by large FC layers.

**Suggested Fix:** Use Global Average Pooling (GAP) instead of flattening + FC. Or use progressively smaller FC layers.

**Example:**
```python
# ❌ BAD: Flatten + huge FC
self.classifier = nn.Sequential(
    nn.Flatten(),           # 7*7*512 = 25088
    nn.Linear(25088, 4096), # 102M parameters!
    nn.ReLU(),
    nn.Linear(4096, 1000),
)

# ✅ GOOD: Global Average Pooling + small FC
self.classifier = nn.Sequential(
    nn.AdaptiveAvgPool2d(1),  # → (batch, 512, 1, 1)
    nn.Flatten(),              # → (batch, 512)
    nn.Linear(512, 1000),     # only 512K parameters
)
```

---

### 2.3 Missing Dropout in Classification Heads

**Description:** Large classification heads (last few FC layers before output) without dropout are prone to overfitting, especially with many classes.

**Severity:** Warning

**Detection:**
- Any Linear layer with `out_features > 256` that is not the final output layer and has no dropout between it and the next layer → flag.

**Suggested Fix:** Add dropout (0.2–0.5) between large FC layers in the classification head.

**Example:**
```python
# ❌ BAD: No dropout in classification head
nn.Sequential(
    nn.Linear(2048, 1024), nn.ReLU(),
    nn.Linear(1024, 512),  nn.ReLU(),
    nn.Linear(512, 100),
)

# ✅ GOOD: Dropout in classification head
nn.Sequential(
    nn.Linear(2048, 1024), nn.ReLU(), nn.Dropout(0.5),
    nn.Linear(1024, 512),  nn.ReLU(), nn.Dropout(0.3),
    nn.Linear(512, 100),
)
```

---

### 2.4 Inefficient Spatial Processing (Missing Downsampling)

**Description:** Using many convolutional layers at high spatial resolution without pooling or strided convolutions. This wastes compute and doesn't build hierarchical features. A 224×224 input processed through 20 conv layers at full resolution is extremely wasteful.

**Severity:** Warning

**Detection:**
- Count consecutive Conv2d layers with stride=1 and no pooling/striding between them. If ≥ 6 at the same spatial resolution → flag.
- If total feature map memory (H × W × C × num_layers) exceeds a threshold → flag.

**Suggested Fix:** Add MaxPool/AvgPool or strided convolution (stride=2) every 2-3 conv layers to reduce spatial dimensions.

**Example:**
```python
# ❌ BAD: 8 conv layers at full resolution
for _ in range(8):
    layers += [nn.Conv2d(64, 64, 3, padding=1), nn.ReLU()]

# ✅ GOOD: Downsample periodically
for i in range(4):
    layers += [nn.Conv2d(64, 64, 3, padding=1), nn.ReLU()]
    layers += [nn.Conv2d(64, 64, 3, padding=1), nn.ReLU()]
    layers += [nn.MaxPool2d(2)]  # halve spatial dims
```

---

### 2.5 Dimension Mismatch Chains

**Description:** Layer output dimensions don't match the next layer's expected input dimensions, causing runtime errors. Common with incorrect padding, stride calculations, or channel changes.

**Severity:** Critical

**Detection:**
- Symbolically trace the tensor shape through the graph. For Conv2d: `H_out = (H_in + 2*pad - kernel) / stride + 1`. If any layer's output shape doesn't match the next layer's expected input → flag.
- For Linear layers: straightforward `in_features` vs previous layer's `out_features`.

**Suggested Fix:** Fix padding, stride, or kernel parameters to produce correct output shapes.

**Example:**
```python
# ❌ BAD: Spatial dimension mismatch
nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=0)  # 32→15
nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=0) # 15→7
nn.Conv2d(256, 512, kernel_size=3, stride=2, padding=0) # 7→3
nn.Conv2d(512, 1024, kernel_size=5, stride=2, padding=0) # 3→0 → ERROR!

# ✅ GOOD: Use padding to maintain expected dimensions
nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1)  # 32→16
nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1) # 16→8
nn.Conv2d(256, 512, kernel_size=3, stride=2, padding=1) # 8→4
nn.Conv2d(512, 1024, kernel_size=3, stride=2, padding=1) # 4→2
```

---

### 2.6 Unbalanced Network Width (Bottleneck Without Purpose)

**Description:** Abruptly narrowing channel dimensions (e.g., 512 → 32 → 512) without a specific purpose (like an autoencoder bottleneck) creates information bottlenecks that lose representational capacity.

**Severity:** Warning

**Detection:**
- For consecutive layers, if channel/hidden dim drops by > 4× and recovers within 2 layers → flag (unless in autoencoder/SE-block context).

**Suggested Fix:** Use gradual dimension changes or remove the unnecessary bottleneck.

**Example:**
```python
# ❌ BAD: Unnecessary bottleneck
nn.Sequential(
    nn.Conv2d(512, 32, 1),   # 16x compression
    nn.ReLU(),
    nn.Conv2d(32, 512, 1),   # 16x expansion
)

# ✅ GOOD: Gradual reduction (if needed)
nn.Sequential(
    nn.Conv2d(512, 256, 1),
    nn.ReLU(),
    nn.Conv2d(256, 512, 1),
)
```

---

### 2.7 Repeated Identical Blocks Without Variation

**Description:** Stacking many identical blocks without any variation in width, kernel size, or resolution. Multi-scale feature extraction requires diversity in receptive field sizes.

**Severity:** Info

**Detection:**
- If > 5 consecutive blocks have identical kernel sizes, channel counts, and no dimension changes → flag as potentially missing multi-scale features.

**Suggested Fix:** Vary kernel sizes (3×3, 5×5, dilated), add squeeze-excitation blocks, or vary channel widths progressively.

---

## 3. Training-Related Red Flags

### 3.1 Architecture Too Complex for Dataset Size

**Description:** A model with far more parameters than the dataset can support leads to severe overfitting. Rule of thumb: you need roughly 5–10× more training samples than model parameters for good generalization (without heavy regularization).

**Severity:** Critical

**Detection:**
- Count total trainable parameters. If `params > dataset_size * 0.1` (without strong regularization like heavy dropout, weight decay, data augmentation) → flag.
- Flag if model has >10M params and dataset has <10K samples.
- Flag if model has >100M params and dataset has <100K samples.

**Suggested Fix:** Reduce model size, use transfer learning, add regularization, or augment data.

**Example:**
```
# ❌ BAD: ResNet-152 (60M params) on 500 images
# → massive overfitting guaranteed

# ✅ GOOD: Pre-trained ResNet-18 with fine-tuning on 500 images
# or a small custom CNN with strong augmentation
```

---

### 3.2 Learning Rate Incompatible with Architecture Depth

**Description:** Using a learning rate that is too high for deep networks causes gradient explosion; too low for shallow networks causes no learning. Deep networks with BN can tolerate higher LRs; networks without BN need lower LRs.

**Severity:** Warning

**Detection:**
- If network depth > 50 and no BN/LN and learning_rate > 0.01 → flag.
- If network depth > 100 and learning_rate > 0.1 (even with BN) → flag without LR warmup.
- If network is shallow (< 5 layers) and learning_rate < 1e-4 → flag as potentially too slow.

**Suggested Fix:** Use learning rate warmup for deep networks, LR schedulers (cosine, step decay), and appropriate base LR (0.1 for ResNets with BN, 1e-3 for Transformers, 1e-4 for fine-tuning).

---

### 3.3 Loss Function / Output Layer Mismatch

**Description:** Using an incompatible loss function and output activation. E.g., using `nn.CrossEntropyLoss` (which applies softmax internally) with a softmax output layer applies softmax twice, producing overconfident, poorly calibrated gradients.

**Severity:** Critical

**Detection:**
- `CrossEntropyLoss` + `Softmax` output → flag (double softmax).
- `BCEWithLogitsLoss` + `Sigmoid` output → flag (double sigmoid).
- `MSELoss` for classification → flag.
- `CrossEntropyLoss` for binary classification → not wrong but flag as unusual (BCE is standard).
- Multi-label classification with `CrossEntropyLoss` (which assumes mutually exclusive classes) → flag.

**Suggested Fix:**
- Multi-class: `CrossEntropyLoss` with raw logits (no softmax in model).
- Binary: `BCEWithLogitsLoss` with raw logits (no sigmoid in model).
- Multi-label: `BCEWithLogitsLoss` with raw logits.
- Regression: `MSELoss` or `L1Loss` with no activation on output.

**Example:**
```python
# ❌ BAD: Double softmax
model = nn.Sequential(..., nn.Linear(512, 10), nn.Softmax(dim=-1))
loss_fn = nn.CrossEntropyLoss()  # applies softmax again!

# ✅ GOOD: Raw logits with CrossEntropyLoss
model = nn.Sequential(..., nn.Linear(512, 10))  # no softmax
loss_fn = nn.CrossEntropyLoss()

# ❌ BAD: Double sigmoid
model = nn.Sequential(..., nn.Linear(512, 1), nn.Sigmoid())
loss_fn = nn.BCEWithLogitsLoss()  # applies sigmoid again!

# ✅ GOOD: Raw logits with BCEWithLogitsLoss
model = nn.Sequential(..., nn.Linear(512, 1))  # no sigmoid
loss_fn = nn.BCEWithLogitsLoss()
```

---

### 3.4 Missing Gradient Clipping for RNN/Transformers

**Description:** RNNs/LSTMs and Transformers are susceptible to gradient explosions during training. Without gradient clipping, training can become unstable.

**Severity:** Warning

**Detection:**
- If architecture contains RNN/LSTM/GRU or Transformer blocks and no gradient clipping is configured → flag.
- Detect by checking for `torch.nn.utils.clip_grad_norm_` or framework equivalent.

**Suggested Fix:** Add gradient clipping (max_norm=1.0 for Transformers, max_norm=5.0 for RNNs).

---

### 3.5 Using MSE Loss for Classification

**Description:** Using Mean Squared Error loss for classification tasks. MSE doesn't penalize confident wrong predictions enough and produces non-convex optimization landscapes for classification.

**Severity:** Critical

**Detection:**
- If output activation is softmax/sigmoid AND loss is MSELoss → flag.
- If task is classification (detected from output dim > 1 + softmax, or binary + sigmoid) AND loss is MSELoss → flag.

**Suggested Fix:** Use CrossEntropyLoss for multi-class, BCEWithLogitsLoss for binary/multi-label.

---

### 3.6 Unbalanced Loss Weights in Multi-Task Learning

**Description:** In multi-task architectures, if loss weights are not balanced, one task dominates training and others receive negligible gradient signal.

**Severity:** Warning

**Detection:**
- If model has multiple heads/outputs and loss weights are all 1.0 (default) without evidence of balancing (uncertainty weighting, GradNorm, etc.) → flag.

**Suggested Fix:** Use uncertainty weighting (Kendall et al. 2018), GradNorm, or manually tuned loss weights based on loss magnitudes.

---

## 4. Efficiency Anti-Patterns

### 4.1 Redundant Consecutive Identical Conv Layers

**Description:** Two consecutive Conv layers with identical kernel size, stride, padding, and groups, with no non-linearity between them, collapse into a single equivalent layer. Even with non-linearity, two 3×3 convs can often be replaced by one 5×5 with fewer parameters.

**Severity:** Info

**Detection:**
- Two consecutive Conv layers with same kernel, stride, padding, groups, and no activation between → flag as linear collapse.
- Three or more consecutive identical Conv layers → flag as potentially redundant.

**Suggested Fix:** Verify each layer contributes non-linear transformation. Consider larger kernel as replacement.

**Example:**
```python
# ❌ BAD: Two convs without activation (linear collapse)
nn.Sequential(
    nn.Conv2d(64, 64, 3, padding=1),
    nn.Conv2d(64, 64, 3, padding=1),  # equivalent to one 5x5 conv
    nn.ReLU(),
)

# ✅ GOOD: Activation between convolutions
nn.Sequential(
    nn.Conv2d(64, 64, 3, padding=1), nn.ReLU(),
    nn.Conv2d(64, 64, 3, padding=1), nn.ReLU(),
)
```

---

### 4.2 Premature Flattening

**Description:** Flattening spatial feature maps too early (before sufficient spatial processing) destroys spatial structure and creates massive parameter counts in subsequent FC layers.

**Severity:** Warning

**Detection:**
- If `nn.Flatten()` appears while spatial dimensions (H, W) are still > 7×7 → flag.
- If flatten is followed by Linear layer with `in_features > 100000` → flag.

**Suggested Fix:** Continue with convolutions/pooling until spatial dims are reduced (e.g., 7×7 or 1×1 via GAP).

**Example:**
```python
# ❌ BAD: Flattening 56×56 feature maps
self.head = nn.Sequential(
    nn.Flatten(),           # 56*56*256 = 802,816
    nn.Linear(802816, 4096) # 3.3B parameters!
)

# ✅ GOOD: Pool first, then flatten
self.head = nn.Sequential(
    nn.AdaptiveAvgPool2d(1),  # → (batch, 256, 1, 1)
    nn.Flatten(),
    nn.Linear(256, 4096),     # 1M parameters
)
```

---

### 4.3 Excessive Use of Large Kernels

**Description:** Using 7×7 or larger kernels when stacks of 3×3 kernels achieve the same receptive field with fewer parameters. Two 3×3 convs = one 5×5 receptive field but with 18/C² parameters vs 25/C².

**Severity:** Info

**Detection:**
- If kernel_size ≥ 5 on a layer where channels > 64 → flag (unless first layer or specific architecture like ConvNeXt).
- Exception: first convolutional layer (e.g., 7×7 stride 2 in ResNet).

**Suggested Fix:** Replace large kernels with stacks of 3×3 kernels.

**Example:**
```python
# ❌ BAD: 7x7 conv in middle of network
nn.Conv2d(256, 256, kernel_size=7, padding=3)  # 49 * 256 * 256 = 3.2M params

# ✅ GOOD: Two 3x3 convs (same receptive field)
nn.Sequential(
    nn.Conv2d(256, 256, kernel_size=3, padding=1),  # 2.3M
    nn.ReLU(),
    nn.Conv2d(256, 256, kernel_size=3, padding=1),  # 2.3M
)  # total 4.6M but with non-linearity between → more powerful
```

**Note:** Recent research (ConvNeXt, 2022) shows depthwise 7×7 kernels can be efficient. The anti-pattern applies to dense (non-depthwise) large kernels.

---

### 4.4 Redundant 1×1 Convolutions Without Purpose

**Description:** A 1×1 conv that maps `C → C` (same channels) without changing dimensions or adding non-linearity is a no-op (with identity init) or adds unnecessary parameters.

**Severity:** Info

**Detection:**
- 1×1 conv with `in_channels == out_channels`, no activation after, and not part of a SE/bottleneck/attention block → flag.

**Suggested Fix:** Remove the redundant layer unless it serves a specific purpose (feature mixing in attention, bottleneck, etc.).

---

### 4.5 Excessive Memory from Large Intermediate Tensors

**Description:** Storing many large intermediate feature maps for backpropagation causes OOM errors. Common in architectures with many parallel branches (e.g., Inception) at high resolution.

**Severity:** Warning

**Detection:**
- Estimate peak memory: sum of all intermediate tensor sizes at the widest point. If > GPU memory threshold → flag.
- Flag architectures with > 10 parallel paths at resolution > 56×56.

**Suggested Fix:** Use gradient checkpointing, reduce parallelism, or downsample earlier.

---

## 5. Task-Specific Rules

### 5.1 CNN for Image Classification: Common Mistakes

#### 5.1.1 No Data Augmentation Awareness

**Description:** Architecture complexity should match augmentation level. Without augmentation, large models overfit quickly on small image datasets.

**Severity:** Warning

**Detection:**
- If model params > 1M and no data augmentation pipeline detected in training config → flag.

#### 5.1.2 Incorrect Input Normalization

**Description:** Missing or incorrect input normalization (ImageNet models expect specific mean/std).

**Severity:** Critical

**Detection:**
- If using a pretrained model and input normalization doesn't match (ImageNet: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) → flag.

#### 5.1.3 Using FC Layers Instead of Conv for Spatial Tasks

**Description:** Using fully connected layers where convolutional layers would be more efficient and spatially aware.

**Severity:** Warning

**Detection:**
- If input is image-shaped (H, W, C) and first operation is Flatten + Linear → flag.

#### 5.1.4 Wrong Pooling for Segmentation

**Description:** Using too much pooling in segmentation architectures destroys spatial information needed for pixel-level predictions.

**Severity:** Warning

**Detection:**
- If task is segmentation (detected from architecture pattern) and spatial resolution is reduced by > 32× without corresponding upsampling path → flag.

---

### 5.2 RNN/LSTM for Sequences: Common Mistakes

#### 5.2.1 Not Using Bidirectional for Non-Causal Tasks

**Description:** Using unidirectional LSTM when the task doesn't require causal (left-to-right only) processing. Bidirectional LSTMs capture both past and future context.

**Severity:** Info

**Detection:**
- If task is not autoregressive generation (e.g., classification, NER, sentiment) and LSTM is unidirectional → suggest bidirectional.

#### 5.2.2 Vanishing Gradient in Long Sequences

**Description:** Standard RNNs (and even LSTMs for very long sequences > 500 steps) struggle with long-range dependencies.

**Severity:** Warning

**Detection:**
- If sequence length > 500 and using standard RNN (not LSTM/GRU) → critical.
- If sequence length > 1000 and using LSTM → suggest Transformer or state-space model.

#### 5.2.3 No Gradient Clipping

**Description:** RNNs are notorious for gradient explosions.

**Severity:** Critical

**Detection:**
- Any RNN/LSTM/GRU architecture without gradient clipping → flag.

#### 5.2.4 Stacking Too Many LSTM Layers

**Description:** More than 3-4 LSTM layers rarely helps and makes training very difficult.

**Severity:** Warning

**Detection:**
- If num_layers > 4 → flag.

#### 5.2.5 Not Handling Variable Length Sequences Properly

**Description:** Not using packed sequences or masking for variable-length inputs, causing the LSTM to process padding tokens.

**Severity:** Critical

**Detection:**
- If input has variable lengths and no packing/masking detected → flag.

---

### 5.3 Transformer Architectures: Common Mistakes

#### 5.3.1 Missing Positional Encoding

**Description:** Transformers have no inherent notion of position. Without positional encoding, the model treats input as a bag of tokens.

**Severity:** Critical

**Detection:**
- If architecture is Transformer-based and no positional encoding (sinusoidal, learned, RoPE, ALiBi) detected → flag.

#### 5.3.2 Wrong Attention Mask for Causal Tasks

**Description:** Using bidirectional (full) attention for autoregressive generation allows the model to peek at future tokens.

**Severity:** Critical

**Detection:**
- If task is autoregressive generation and no causal mask detected → flag.

#### 5.3.3 MHA Heads Not Dividing Embedding Dim

**Description:** Multi-head attention requires `d_model % num_heads == 0`. If not divisible, dimensions don't align.

**Severity:** Critical

**Detection:**
- `d_model % num_heads != 0` → flag.

#### 5.3.4 Missing Layer Normalization

**Description:** Transformers require layer normalization for stable training. Missing it causes training instability.

**Severity:** Critical

**Detection:**
- Transformer block without LayerNorm → flag.

#### 5.3.5 Wrong Pre/Post-LN Placement

**Description:** Original Transformer uses Post-LN (attention → add → LN). Modern practice uses Pre-LN (LN → attention → add) for more stable training.

**Severity:** Info

**Detection:**
- Detect Post-LN pattern → suggest Pre-LN for better training stability.

#### 5.3.6 Excessive Sequence Length Without Attention Optimization

**Description:** Using full O(n²) attention for sequences > 4096 tokens is prohibitively expensive.

**Severity:** Warning

**Detection:**
- If seq_len > 4096 and attention is standard (not sparse, linear, flash, or sliding window) → flag.

**Suggested Fix:** Use Flash Attention, sparse attention, sliding window attention, or linear attention variants.

#### 5.3.7 Missing Residual Connections in Transformer Blocks

**Description:** Transformer blocks MUST have residual connections around both attention and FFN sub-layers.

**Severity:** Critical

**Detection:**
- Transformer block without add/residual around attention or FFN → flag.

#### 5.3.8 FFN Expansion Ratio Too Small or Too Large

**Description:** Standard Transformer FFN expands d_model by 4×. Significantly deviating hurts capacity.

**Severity:** Info

**Detection:**
- If FFN hidden dim / d_model < 2 or > 8 → flag as unusual.

---

### 5.4 Autoencoder Architectures: Common Mistakes

#### 5.4.1 No Bottleneck (Undercomplete Constraint)

**Description:** If the latent space has equal or greater dimensionality than the input, the autoencoder can learn the identity function without extracting useful features.

**Severity:** Critical

**Detection:**
- If latent_dim ≥ input_dim → flag.

**Suggested Fix:** Reduce latent dimension to force compression (typically 1/4 to 1/100 of input dim).

#### 5.4.2 Decoder Doesn't Mirror Encoder

**Description:** In standard autoencoders, the decoder should roughly mirror the encoder architecture. Asymmetry can cause poor reconstruction.

**Severity:** Info

**Detection:**
- If encoder and decoder have significantly different numbers of layers or capacity → flag.

#### 5.4.3 Missing Reconstruction Loss Scaling

**Description:** Using raw pixel MSE loss without considering the scale. High-dimensional outputs (e.g., 256×256×3) produce very large MSE values that dominate other loss terms (e.g., KL divergence in VAE).

**Severity:** Warning

**Detection:**
- If output dim > 1000 and loss is MSE without normalization → flag.

#### 5.4.4 VAE: KL Collapse (KL → 0)

**Description:** In Variational Autoencoders, the KL divergence term can collapse to zero, meaning the model ignores the latent space and just memorizes.

**Severity:** Critical

**Detection:**
- Not directly detectable from architecture alone, but flag if VAE has no KL annealing, free bits, or β scheduling configured.

#### 5.4.5 Transposed Convolution Checkerboard Artifacts

**Description:** Using transposed convolutions (deconvolutions) for upsampling causes checkerboard artifacts due to uneven overlap.

**Severity:** Warning

**Detection:**
- If decoder uses ConvTranspose2d with stride > 1 → flag.

**Suggested Fix:** Use resize (bilinear/nearest) + regular convolution instead.

**Example:**
```python
# ❌ BAD: Transposed convolution (checkerboard artifacts)
nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1)

# ✅ GOOD: Upsample + Conv
nn.Sequential(
    nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
    nn.Conv2d(256, 128, kernel_size=3, padding=1),
)
```

---

## 6. Calculating FLOPs from Layer Parameters

### 6.1 Fully Connected (Linear) Layer

```
FLOPs = 2 × in_features × out_features  (multiply + accumulate per output)
       + out_features                     (bias addition, if bias=True)
```

**Simplified:** `FLOPs ≈ 2 × in × out`

### 6.2 Convolutional Layer

```
FLOPs = 2 × C_in × K_h × K_w × C_out × H_out × W_out
       + C_out × H_out × W_out  (bias, if present)
```

Where:
- `C_in` = input channels
- `K_h × K_w` = kernel size
- `C_out` = output channels (filters)
- `H_out × W_out` = output spatial dimensions
- Factor of 2: one multiply + one add per operation

**Simplified:** `FLOPs = 2 × C_in × K² × C_out × H_out × W_out`

### 6.3 Depthwise Separable Convolution

```
# Depthwise part
FLOPs_dw = 2 × C_in × K_h × K_w × H_out × W_out  (×1 multiplier, not C_out)

# Pointwise part
FLOPs_pw = 2 × C_in × 1 × 1 × C_out × H_out × W_out

# Total
FLOPs = FLOPs_dw + FLOPs_pw
```

**Efficiency ratio vs standard conv:** approximately `1/C_out + 1/K²` → ~8-9× less for 3×3 conv.

### 6.4 Batch Normalization

```
FLOPs = 2 × C × H × W  (mean + variance in training)
       + 4 × C × H × W  (normalize + scale + shift)
```

**Simplified:** `FLOPs ≈ 6 × C × H × W` (training), `≈ 2 × C × H × W` (inference)

### 6.5 Attention Layer (Multi-Head)

```
# Q, K, V projections
FLOPs_proj = 3 × 2 × d_model × d_model × seq_len

# Attention scores: Q × K^T
FLOPs_attn = 2 × num_heads × seq_len × seq_len × (d_model / num_heads)

# Attention × V
FLOPs_out = 2 × num_heads × seq_len × (d_model / num_heads) × seq_len

# Output projection
FLOPs_o = 2 × d_model × d_model × seq_len

# Total (per layer)
FLOPs = FLOPs_proj + FLOPs_attn + FLOPs_out + FLOPs_o
      ≈ 8 × d_model² × seq_len + 4 × d_model × seq_len²
```

### 6.6 LSTM Layer

```
FLOPs = 8 × (input_size × hidden_size + hidden_size × hidden_size) × seq_len
       + 4 × hidden_size × seq_len  (element-wise ops)
```

Factor of 8: 4 gates × (2 matrix ops: input + hidden)

### 6.7 Practical FLOPs Counting (PyTorch)

```python
# Using fvcore (Meta)
from fvcore.nn import FlopCountAnalysis
flops = FlopCountAnalysis(model, input_tensor)
print(f"Total FLOPs: {flops.total()}")

# Using thop
from thop import profile
flops, params = profile(model, inputs=(input_tensor,))
print(f"FLOPs: {flops}, Params: {params}")

# Using torchinfo
from torchinfo import summary
summary(model, input_size=(1, 3, 224, 224))
```

---

## 7. Estimating Model Memory Footprint

### 7.1 Parameter Memory

```
param_memory = num_params × bytes_per_param
```

| Precision | Bytes/Param | 1M params |
|-----------|-------------|-----------|
| FP32 | 4 | 4 MB |
| FP16/BF16 | 2 | 2 MB |
| INT8 | 1 | 1 MB |
| INT4 | 0.5 | 0.5 MB |

### 7.2 Optimizer State Memory

| Optimizer | States per param | Total bytes (FP32) |
|-----------|------------------|---------------------|
| SGD (no momentum) | 0 | 4 bytes/param |
| SGD + momentum | 1 | 8 bytes/param |
| Adam/AdamW | 2 (m, v) | 12 bytes/param |

**Adam memory:** `num_params × (4 + 4 + 4) = 12 bytes/param` (param + first moment + second moment)

### 7.3 Activation Memory (Training)

For a batch of size B through a layer:

```
activation_memory = B × C × H × W × bytes_per_element
```

**Peak activation memory** ≈ sum of all intermediate tensors that must be saved for backward pass.

**Rule of thumb:** For a typical CNN, peak activation memory ≈ 2-4× parameter memory during training.

### 7.4 Gradient Memory

```
gradient_memory = num_params × bytes_per_param  (same precision as params)
```

### 7.5 Total Training Memory

```
total_memory = param_memory + gradient_memory + optimizer_state_memory + activation_memory
```

**Example for ResNet-50:**
- Parameters: 25.6M × 4 bytes = 102 MB
- Gradients: 25.6M × 4 bytes = 102 MB
- Adam states: 25.6M × 8 bytes = 205 MB
- Activations (batch=32): ~600 MB
- **Total: ~1 GB** (without mixed precision)

### 7.6 Inference Memory

```
inference_memory = param_memory + max_layer_activation_memory
```

Much simpler: just parameters + one batch of activations at the widest layer.

### 7.7 Practical Memory Estimation (PyTorch)

```python
import torch

def estimate_model_memory(model, input_size, batch_size=1, precision='fp32'):
    """Estimate GPU memory for training."""
    bytes_per_param = {'fp32': 4, 'fp16': 2, 'bf16': 2}[precision]

    # Parameter memory
    param_mem = sum(p.numel() for p in model.parameters()) * bytes_per_param

    # Gradient memory (same as params)
    grad_mem = param_mem

    # Optimizer states (Adam: 2 extra copies)
    optim_mem = param_mem * 2  # m and v states

    # Rough activation estimate using forward hook
    activation_sizes = []
    def hook(module, inp, out):
        if isinstance(out, torch.Tensor):
            activation_sizes.append(out.numel() * bytes_per_param)
        elif isinstance(out, (tuple, list)):
            for o in out:
                if isinstance(o, torch.Tensor):
                    activation_sizes.append(o.numel() * bytes_per_param)

    hooks = [m.register_forward_hook(hook) for m in model.modules()]
    dummy = torch.randn(batch_size, *input_size)
    model(dummy)
    for h in hooks:
        h.remove()

    activation_mem = sum(activation_sizes)

    total = param_mem + grad_mem + optim_mem + activation_mem
    return {
        'parameters_MB': param_mem / 1e6,
        'gradients_MB': grad_mem / 1e6,
        'optimizer_MB': optim_mem / 1e6,
        'activations_MB': activation_mem / 1e6,
        'total_MB': total / 1e6,
    }
```

---

## 8. Estimating Training Time

### 8.1 Theoretical FLOP-Based Estimate

```
time_per_step = total_FLOPs × batch_size / (GPU_TFLOPS × 1e12 × utilization)
```

Where:
- `total_FLOPs` = forward + backward FLOPs (≈ 3× forward FLOPs)
- `GPU_TFLOPS` = peak TFLOPS of GPU (e.g., A100 = 312 TFLOPS FP16)
- `utilization` = typical 0.3-0.7 (memory bandwidth, kernel launch overhead)

### 8.2 Memory-Bandwidth Bound vs Compute-Bound

**Arithmetic Intensity** = FLOPs / bytes_transferred

- If arithmetic intensity < GPU's ops:byte ratio → **memory-bound** (common for small layers, embedding lookups)
- If arithmetic intensity > GPU's ops:byte ratio → **compute-bound** (common for large matrix multiplies)

**A100:** 312 TFLOPS / 2 TB/s bandwidth = 156 ops/byte ratio

### 8.3 Practical Training Time Estimate

```python
def estimate_training_time(
    flops_per_sample,      # FLOPs for one forward pass
    dataset_size,          # number of training samples
    batch_size,
    gpu_tflops,            # peak TFLOPS (e.g., 312 for A100 FP16)
    gpu_memory_gb,         # GPU memory
    num_gpus=1,
    num_epochs=100,
    utilization=0.4,       # typical GPU utilization
    overhead_factor=1.2,   # data loading, communication, etc.
):
    # Forward + backward ≈ 3× forward
    flops_per_step = flops_per_sample * batch_size * 3

    # Steps per epoch
    steps_per_epoch = dataset_size // batch_size

    # Total steps
    total_steps = steps_per_epoch * num_epochs

    # Time per step (seconds)
    effective_tflops = gpu_tflops * utilization * num_gpus
    time_per_step = flops_per_step / (effective_tflops * 1e12)

    # Total time
    total_time = total_steps * time_per_step * overhead_factor

    return {
        'total_hours': total_time / 3600,
        'steps_per_epoch': steps_per_epoch,
        'total_steps': total_steps,
        'time_per_step_ms': time_per_step * 1000,
    }
```

### 8.4 Rules of Thumb

| Model | Params | FLOPs/sample | A100 days (1 GPU) |
|-------|--------|-------------|-------------------|
| ResNet-50 | 25.6M | 4.1G | ~1.5 days (ImageNet) |
| BERT-base | 110M | ~50G | ~4 days |
| BERT-large | 340M | ~150G | ~12 days |
| GPT-2 | 1.5B | ~1.5T | ~months |
| ViT-L/16 | 307M | ~100G | ~8 days (ImageNet) |

---

## 9. Model Card Standard Fields

Based on Google's Model Cards (Mitchell et al., 2019) and Hugging Face's extended format:

### 9.1 Required Fields

| Field | Description |
|-------|-------------|
| **Model Name** | Unique identifier |
| **Model Version** | Semantic version or commit hash |
| **Model Type** | Architecture family (CNN, Transformer, etc.) |
| **Model Description** | Brief description of what the model does |
| **Model Owner** | Person/org responsible |
| **License** | Open-source license or terms of use |

### 9.2 Intended Use

| Field | Description |
|-------|-------------|
| **Primary Intended Uses** | What the model is designed for |
| **Primary Intended Users** | Target audience (researchers, production, etc.) |
| **Out-of-Scope Uses** | What the model should NOT be used for |
| **Factors** | Relevant factors (demographic, environmental) |

### 9.3 Training Details

| Field | Description |
|-------|-------------|
| **Training Data** | Dataset(s) used, with links |
| **Training Procedure** | Optimizer, LR, schedule, epochs, batch size |
| **Training Hardware** | GPU/TPU type, number of devices |
| **Training Time** | Wall-clock time |
| **Carbon Emitted** | Estimated CO₂ (optional, using tools like CodeCarbon) |

### 9.4 Evaluation Details

| Field | Description |
|-------|-------------|
| **Evaluation Data** | Datasets and splits used |
| **Metrics** | Performance metrics (accuracy, F1, BLEU, etc.) |
| **Results** | Quantitative results per metric |
| **Baseline Comparisons** | Compared against what baselines |

### 9.5 Ethical Considerations

| Field | Description |
|-------|-------------|
| **Sensitive Data** | Does the model use sensitive data? |
| **Risks** | Known risks and failure modes |
| **Bias Analysis** | Bias evaluation results |
| **Harmful Outputs** | Potential for harmful outputs |

### 9.6 Technical Specifications

| Field | Description |
|-------|-------------|
| **Architecture** | Detailed architecture description |
| **Parameters** | Total and per-component parameter counts |
| **FLOPs** | Computational cost |
| **Model Size** | File size (MB/GB) |
| **Input Format** | Expected input shape and type |
| **Output Format** | Output shape and type |
| **Framework** | PyTorch, TensorFlow, JAX, etc. |
| **Precision** | FP32, FP16, BF16, INT8, etc. |

### 9.7 Model Card YAML Template

```yaml
model_card:
  name: "my-model-v1"
  version: "1.0.0"
  type: "image-classification"
  description: "ResNet-50 fine-tuned on custom medical imaging dataset"
  owner: "ML Team"
  license: "Apache-2.0"

  intended_use:
    primary_uses: "Classifying chest X-rays for pneumonia detection"
    primary_users: "Radiologists and medical imaging researchers"
    out_of_scope: "Not for use as sole diagnostic tool; not validated for pediatric cases"

  training:
    data:
      - name: "ChestX-ray14"
        url: "https://nihcc.app.box.com/v/ChestXray-NIHCC"
        size: 112120 images
    procedure:
      optimizer: "AdamW"
      learning_rate: 1e-4
      lr_schedule: "cosine"
      batch_size: 64
      epochs: 30
      weight_decay: 0.01
    hardware: "4× NVIDIA A100 80GB"
    training_time: "6 hours"
    carbon_emitted: "2.3 kg CO₂"

  evaluation:
    data:
      - name: "Test split (20%)"
        size: 22424 images
    metrics:
      - name: "AUC-ROC"
        value: 0.943
      - name: "F1-Score"
        value: 0.891
    baselines:
      - name: "DenseNet-121"
        auc: 0.921

  ethics:
    sensitive_data: true  # medical images
    risks: "May exhibit bias across demographics; requires clinical validation"
    bias_analysis: "Evaluated across age groups and sexes; see appendix"

  technical:
    architecture: "ResNet-50 with modified classification head"
    parameters: 25600000
    flops_per_sample: 4.1e9
    model_size_mb: 98
    input_format: "(B, 3, 224, 224) normalized RGB"
    output_format: "(B, 14) sigmoid probabilities"
    framework: "PyTorch 2.0"
    precision: "FP32"
```

---

## Quick Reference: Severity Summary

### Critical (Must Fix)
| ID | Anti-Pattern |
|----|-------------|
| 1.1 | Missing activation function |
| 1.2 | Sigmoid/tanh in deep networks |
| 1.3 | ReLU in RNN gates |
| 2.1 | Deep network without skip connections |
| 2.5 | Dimension mismatch chains |
| 3.1 | Architecture too complex for dataset |
| 3.3 | Loss/output mismatch (double softmax, etc.) |
| 3.5 | MSE loss for classification |
| 5.1.2 | Incorrect input normalization |
| 5.2.3 | No gradient clipping for RNN |
| 5.3.1 | Missing positional encoding |
| 5.3.2 | Wrong attention mask |
| 5.3.3 | MHA heads don't divide d_model |
| 5.3.4 | Missing LayerNorm |
| 5.3.7 | Missing residual in Transformer |
| 5.4.1 | Autoencoder with no bottleneck |

### Warning (Should Fix)
| ID | Anti-Pattern |
|----|-------------|
| 1.4 | Missing BatchNorm in deep CNNs |
| 1.6 | Dropout in wrong location |
| 1.7 | Incorrect weight initialization |
| 2.2 | Parameter explosion in FC layers |
| 2.3 | Missing dropout in classification heads |
| 2.4 | Inefficient spatial processing |
| 2.6 | Unbalanced network width |
| 3.2 | LR incompatible with depth |
| 3.4 | Missing gradient clipping (general) |
| 3.6 | Unbalanced multi-task loss |
| 4.2 | Premature flattening |
| 4.5 | Excessive memory from intermediates |
| 5.1.1 | No augmentation awareness |
| 5.1.3 | FC instead of conv for images |
| 5.1.4 | Wrong pooling for segmentation |
| 5.2.4 | Too many LSTM layers |
| 5.3.6 | Long seq without efficient attention |
| 5.4.3 | Missing loss scaling in autoencoder |
| 5.4.5 | Transposed conv checkerboard |

### Info (Consider Fixing)
| ID | Anti-Pattern |
|----|-------------|
| 1.5 | BN placement (before/after activation) |
| 1.8 | Bias with BatchNorm |
| 2.7 | Repeated identical blocks |
| 4.1 | Redundant consecutive convs |
| 4.3 | Excessive large kernels |
| 4.4 | Redundant 1×1 convolutions |
| 5.2.1 | Unidirectional LSTM for non-causal tasks |
| 5.4.2 | Decoder doesn't mirror encoder |
| 5.3.8 | FFN expansion ratio unusual |

---

## Appendix A: Layer Counting Rules

When counting "depth" for severity thresholds:

| Architecture | Depth metric |
|---|---|
| Plain CNN | Number of Conv layers |
| ResNet | Number of conv layers in longest path (not counting shortcuts) |
| Transformer | Number of Transformer blocks |
| LSTM | Number of LSTM layers (×2 for bidirectional) |
| MLP | Number of Linear layers |

## Appendix B: Common Architecture Patterns to Recognize

### Residual Block
```
x → Conv → BN → ReLU → Conv → BN → (+x) → ReLU
  └──────────────────────────────────────────┘
```

### Transformer Block (Pre-LN)
```
x → LN → MHA → (+x) → LN → FFN → (+x)
```

### Depthwise Separable Conv
```
x → DepthwiseConv(C_in, K) → BN → ReLU → PointwiseConv(C_in, C_out) → BN → ReLU
```

### Squeeze-Excitation Block
```
x → GAP → FC → ReLU → FC → Sigmoid → (×x)
```

### Inception Module
```
x → ├─ 1×1 Conv ─────────────────────────┤
    ├─ 1×1 Conv → 3×3 Conv ──────────────┤→ Concat
    ├─ 1×1 Conv → 5×5 Conv ──────────────┤
    └─ MaxPool → 1×1 Conv ───────────────┘
```

---

*Document version: 1.0 | Generated: 2026-06-25*
*References: He et al. 2016 (ResNet), Vaswani et al. 2017 (Attention), Ioffe & Szegedy 2015 (BN), Kingma & Ba 2015 (Adam), Mitchell et al. 2019 (Model Cards)*
