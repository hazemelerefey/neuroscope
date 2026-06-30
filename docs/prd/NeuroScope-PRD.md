# NeuroScope — Product Requirements Document (PRD)

**Product:** NeuroScope Visual Builder
**Version:** 1.0 (Phase 1 — CNN v16)
**Date:** June 29, 2026
**Owner:** Hazem Khaled

---

## 1. Product Overview

### What is NeuroScope?

NeuroScope is a **visual model builder** for deep learning. Users configure neural network architectures through an interactive 3D interface and export ready-to-run Jupyter Notebooks — no code writing required.

### The Problem

ML students can't see what they're building. They write layers in code, train models, and hope for the best. When something goes wrong, they have no way to know without senior engineering review.

### The Solution

A visual, interactive 3D workspace where:
- Users select a model → it appears as a glowing 3D machine
- Users configure hyperparameters → each one is a satellite module with visual feedback
- Code generates live → users see exactly what's being built
- Everything is educational → users learn while building

### The Metaphor

**Powering up a machine.** Dark to light. Disconnected to connected. Empty to complete. Every visual change = a line of code written.

---

## 2. User Personas

### Primary: ML Student (Africa)

| Attribute | Detail |
|-----------|--------|
| **Name** | Amina, 22, Computer Science student |
| **Location** | Nairobi, Kenya |
| **Experience** | Beginner-intermediate in Python, basic ML knowledge |
| **Pain Point** | Doesn't understand hyperparameters; writes code by copying tutorials |
| **Goal** | Build a working CNN for her class project without making basic mistakes |
| **Environment** | Uses Colab on a university computer; limited GPU access |

### Secondary: ML Educator

| Attribute | Detail |
|-----------|--------|
| **Name** | Dr. Okafor, 45, University lecturer |
| **Location** | Lagos, Nigeria |
| **Experience** | Expert in ML; teaches introductory deep learning |
| **Pain Point** | Students don't understand *why* they choose certain hyperparameters |
| **Goal** | A tool that teaches while students build; can be used in lab sessions |
| **Environment** | University computer lab; projector for demonstrations |

### Tertiary: Self-Taught Developer

| Attribute | Detail |
|-----------|--------|
| **Name** | Karim, 28, software developer learning ML |
| **Location** | Cairo, Egypt |
| **Experience** | Strong in web dev; new to deep learning |
| **Pain Point** | Overwhelmed by options; doesn't know where to start |
| **Goal** | Build his first CNN for a personal project |
| **Environment** | Personal laptop; uses YouTube tutorials |

---

## 3. User Stories

### 3.1 Workspace & Model Selection

| ID | User Story | Priority |
|----|-----------|----------|
| US-01 | As a user, I want to see an empty workspace when I open the app, so I know where to start | P0 |
| US-02 | As a user, I want to click a `+` button to see available models, so I can choose one easily | P0 |
| US-03 | As a user, I want to drag a model from a side panel and drop it on the workspace, so it feels like building something | P0 |
| US-04 | As a user, I want to see the model "power on" with a visual animation when I select it, so it feels like I'm activating a machine | P0 |
| US-05 | As a user, I want to see the model name and type displayed on the 3D engine, so I know what I'm working with | P0 |

### 3.2 Core Engine & Develop Mode

| ID | User Story | Priority |
|----|-----------|----------|
| US-06 | As a user, I want to click the core engine to see options (Change Model, Custom), so I can modify my selection | P0 |
| US-07 | As a user, I want to open a "Develop Mode" to see all model layers, so I can understand the architecture | P0 |
| US-08 | As a user, I want to freeze/unfreeze layers in Develop Mode, so I can control which layers train | P0 |
| US-09 | As a user, I want to see the Head layer prominently in both the main UI and Develop Mode, so I understand the output | P0 |
| US-10 | As a user, I want to see what activation function the Head layer uses, so I know what the model outputs | P0 |

### 3.3 Extensions (Hyperparameters)

| ID | User Story | Priority |
|----|-----------|----------|
| US-11 | As a user, I want to see extension blocks around the core engine, so I know what I need to configure | P0 |
| US-12 | As a user, I want to click an extension to see all available options, so I can choose the right one | P0 |
| US-13 | As a user, I want to read a simple explanation of each option, so I understand what it does | P0 |
| US-14 | As a user, I want to know when to use each option, so I can make an informed decision | P0 |
| US-15 | As a user, I want to know what happens if I choose the wrong option, so I avoid mistakes | P0 |
| US-16 | As a user, I want to see the extension glow and its cable light up after I configure it, so I feel progress | P0 |
| US-17 | As a user, I want to change an extension's configuration at any time, so I can experiment | P0 |

### 3.4 Info Panel

| ID | User Story | Priority |
|----|-----------|----------|
| US-18 | As a user, I want to see a summary of my model's details in a panel, so I can review my configuration | P0 |
| US-19 | As a user, I want the info panel to update every time I configure an extension, so I see the cumulative effect | P0 |
| US-20 | As a user, I want the info to be in brief points, not long paragraphs, so I can scan it quickly | P0 |

### 3.5 Notebook & Code

| ID | User Story | Priority |
|----|-----------|----------|
| US-21 | As a user, I want to see the generated code in a collapsible window, so I can learn what's being built | P0 |
| US-22 | As a user, I want the code to update live when I change any extension, so I see the connection between visuals and code | P0 |
| US-23 | As a user, I want the notebook to open automatically when I make a change, so I don't miss the code update | P0 |
| US-24 | As a user, I want to edit the code in the notebook, so I can make manual adjustments | P0 |
| US-25 | As a user, I want the notebook to close when I go back to the workspace, so it doesn't block my view | P0 |

### 3.6 Export

| ID | User Story | Priority |
|----|-----------|----------|
| US-26 | As a user, I want to export my model as a Jupyter Notebook, so I can run it on Colab | P0 |
| US-27 | As a user, I want the notebook to include comments explaining each code block, so I understand what I'm running | P0 |
| US-28 | As a user, I want placeholder comments for dataset import, so I know where to add my data | P0 |
| US-29 | As a user, I want to export as YAML, so I can use the model definition in other tools | P1 |

---

## 4. Information Architecture

### 4.1 Page Structure

```
┌─────────────────────────────────────────────────────────┐
│  NeuroScope                              [?] [Settings] │
├──────────────────────────────────┬──────────────────────┤
│                                  │                      │
│         WORKSPACE                │   RIGHT PANEL        │
│         (3D Canvas)              │   (Collapsible)      │
│                                  │                      │
│    ┌─────────┐                   │   Model Families:    │
│    │ Core    │───┐               │   ┌──────────────┐   │
│    │ Engine  │   │               │   │ CNN v16      │   │
│    └─────────┘   │               │   └──────────────┘   │
│         │        │               │                      │
│    ┌────┴────┐   │               │   (Hidden after      │
│    │Extension│   │               │    model selected)    │
│    │ Blocks  │   │               │                      │
│    └─────────┘   │               │                      │
│                  │               │                      │
│                  │               │                      │
│                  │               │                      │
├──────────────────┴───────────────┴──────────────────────┤
│                    INFO PANEL                           │
│  Model: CNN v16 | Head: Softmax | Optimizer: — | ...   │
└─────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│  NOTEBOOK (Collapsible)  │  ← Top-right corner
│  # Model                 │
│  model = CNNv16()        │
│  # Optimizer             │
│  optimizer = 'AdamW'     │
│  ...                     │
└──────────────────────────┘
```

### 4.2 Navigation Flow

```
App Load
    │
    ▼
Empty Workspace + Right Panel (Model List)
    │
    ├── Click + ──→ Model Selection Menu
    │                    │
    │                    ▼
    │              Select CNN v16
    │                    │
    │                    ▼
    │              Core Engine Activates
    │              Extensions Load
    │              Right Panel Hides
    │              Notebook Opens
    │
    └── Drag from Panel ──→ Drop on Workspace
                               │
                               ▼
                         Core Engine Activates
                         Extensions Load
                         Right Panel Hides
                         Notebook Opens

Then:
    Click Extension ──→ Right Panel Opens (Extension Config)
                            │
                            ▼
                      Select Option + Apply
                            │
                            ▼
                      Code Injects
                      Extension Glows
                      Info Panel Updates
                      Notebook Updates

Click Core Engine ──→ Context Menu
                        ├── Change Model
                        └── Custom (Develop Mode)
```

---

## 5. Visual Design Specification

### 5.1 Design System

| Element | Specification |
|---------|--------------|
| **Background** | Pure black (#000000) or very dark (#0a0a0a) |
| **Primary Font** | Orbitron (headings), Inter (body text) |
| **Style** | Cyberpunk 2077 aesthetic — sharp edges, neon glow, floating particles |

### 5.2 Color Palette

| Color | Hex | Category | Usage |
|-------|-----|----------|-------|
| Blue | #00d4ff | Core | Core engine, model label, primary glow |
| Green | #00ff88 | Training | Optimizer, Activation, Loss extensions |
| Purple | #b44dff | Data | Augmentation, NMS extensions |
| Yellow | #ffd700 | Functional | Resolution, Batch Size, Epochs extensions |
| White | #ffffff | Text | Labels, descriptions |
| Gray | #666666 | Disabled | Inactive extensions, placeholder text |

### 5.3 3D Elements

| Element | Visual | Behavior |
|---------|--------|----------|
| **Core Engine** | Metallic cube with circuit lines | Pulses blue when active; model label on surface |
| **Extension Block** | Smaller cube with category color border | Dark when unconfigured; glows when configured |
| **Cable** | Thick line from extension to core engine | Dark when disconnected; pulses with category color when connected |
| **Head Layer** | Glowing ring on top of core engine | Always visible; shows activation function |
| **Particles** | Floating dots around the scene | Subtle movement; clear away when model is active |

### 5.4 Size Complexity

| Model Size | 3D Representation |
|------------|-------------------|
| Small (fewer layers) | Simple cube, minimal surface detail |
| Medium | Cube with additional geometric layers |
| Large (more layers) | Complex cube with multiple surface layers, more glow |

---

## 6. Extension Specifications — CNN v16

### 6.1 Optimizer Extension

**Category:** Training (Green)
**Icon:** ⚡

| Option | Code | Description | When to Use | Consequences |
|--------|------|-------------|-------------|--------------|
| SGD | `optimizer = 'SGD'` | Stochastic Gradient Descent — the classic | When you have a well-tuned learning rate schedule | Slow convergence; may get stuck in local minima |
| Adam | `optimizer = 'Adam'` | Adaptive learning rate for each parameter | Good default for most tasks | Can overfit; weight decay not properly decoupled |
| AdamW | `optimizer = 'AdamW'` | Adam with decoupled weight decay | Best for modern architectures; default choice | Slightly more compute than Adam |
| RMSprop | `optimizer = 'RMSprop'` | Adaptive learning rate by dividing by running average | Good for RNNs; rarely used for CNNs | Not ideal for image classification |

### 6.2 Activation Function Extension

**Category:** Training (Green)
**Icon:** 🔥

| Option | Code | Description | When to Use | Consequences |
|--------|------|-------------|-------------|--------------|
| ReLU | `activation = 'relu'` | Rectified Linear Unit — max(0, x) | Classic choice; simple and fast | "Dying ReLU" problem — neurons can permanently output 0 |
| LeakyReLU | `activation = 'leaky_relu'` | Like ReLU but allows small negative values | When you have dying ReLU problems | Slightly more compute than ReLU |
| SiLU | `activation = 'silu'` | Sigmoid Linear Unit (Swish) — x * sigmoid(x) | Modern choice; smooth gradient | More compute than ReLU |
| Mish | `activation = 'mish'` | Self-regularized non-monotonic function | State-of-the-art for image tasks | More compute; less interpretable |
| GELU | `activation = 'gelu'` | Gaussian Error Linear Unit | Used in transformers; good for fine-tuning | More compute than ReLU |

### 6.3 Loss Function Extension

**Category:** Training (Green)
**Icon:** 💚

| Option | Code | Description | When to Use | Consequences |
|--------|------|-------------|-------------|--------------|
| CrossEntropy | `loss = 'CrossEntropyLoss()'` | Standard classification loss | Default for multi-class classification | Doesn't handle class imbalance well |
| FocalLoss | `loss = 'FocalLoss()'` | Down-weights easy examples, focuses on hard ones | When dataset has class imbalance | More complex; needs gamma tuning |
| LabelSmoothing | `loss = 'CrossEntropyLoss(label_smoothing=0.1)'` | Prevents overconfident predictions | When model is overfitting | Slightly reduces peak accuracy |

### 6.4 Learning Rate Extension

**Category:** Training (Green)
**Icon:** 📈

| Option | Code | Description | When to Use | Consequences |
|--------|------|-------------|-------------|--------------|
| 0.1 | `lr0 = 0.1` | High learning rate | Fine-tuning with pretrained weights | May overshoot; unstable training |
| 0.01 | `lr0 = 0.01` | Medium learning rate | Training from scratch with SGD | Good balance for most cases |
| 0.001 | `lr0 = 0.001` | Low learning rate | Default for Adam/AdamW | Safe but may be slow |
| 0.0001 | `lr0 = 0.0001` | Very low learning rate | Fine-tuning; final training stages | Very slow convergence |

### 6.5 Batch Size Extension

**Category:** Functional (Yellow)
**Icon:** 📦

| Option | Code | Description | When to Use | Consequences |
|--------|------|-------------|-------------|--------------|
| 8 | `batch = 8` | Small batch | Low GPU memory | Noisy gradients; slower training |
| 16 | `batch = 16` | Medium batch | Good default for most GPUs | Balanced |
| 32 | `batch = 32` | Large batch | High GPU memory | Smoother gradients; may generalize worse |
| 64 | `batch = 64` | Very large batch | Multi-GPU setups | May need learning rate scaling |
| 128 | `batch = 128` | Huge batch | Large-scale training | Requires learning rate warmup |

### 6.6 Epochs Extension

**Category:** Functional (Yellow)
**Icon:** 🔄

| Option | Code | Description | When to Use | Consequences |
|--------|------|-------------|-------------|--------------|
| 50 | `epochs = 50` | Quick training | Testing/debugging | May underfit |
| 100 | `epochs = 100` | Standard training | Small datasets | Good starting point |
| 200 | `epochs = 200` | Long training | Medium datasets | Better convergence |
| 500 | `epochs = 500` | Very long training | Large datasets with augmentation | Needs early stopping |

### 6.7 Data Augmentation Extension

**Category:** Data (Purple)
**Icon:** 🟣

| Option | Code | Description | When to Use | Consequences |
|--------|------|-------------|-------------|--------------|
| None | `# No augmentation` | No data augmentation | When dataset is already large and diverse | Overfitting risk |
| Basic | `transforms.RandomHorizontalFlip()` | Horizontal flip + rotation | Small datasets; general use | May not help with orientation-sensitive data |
| Advanced | `transforms.Compose([...])` | Flip, rotate, color jitter, crop | Medium datasets; need more diversity | May introduce unrealistic samples |
| Custom | `# User-defined pipeline` | User writes their own | Advanced users | Requires knowledge of augmentations |

---

## 7. Code Generation Template — CNN v16

### Generated Notebook Structure

```python
# ============================================
# NeuroScope — CNN v16 Training Notebook
# Generated by NeuroScope Visual Builder
# ============================================

# [1] Environment Setup
# If running locally, uncomment and install:
# !pip install torch torchvision

# [2] Dataset Import
# TODO: Add your dataset import here
# Example:
# from torchvision import datasets, transforms
# train_dataset = datasets.ImageFolder('path/to/train', transform=train_transform)

# [3] Imports
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms

# [4] Model Definition — CNN v16
class CNNv16(nn.Module):
    def __init__(self, num_classes=10):
        super(CNNv16, self).__init__()
        # ... 16 layers defined here
        # Layer 1: Conv2d(3, 64, 3, padding=1)
        # Layer 2: BatchNorm2d(64)
        # ... etc.
        # Head: Linear(in_features, num_classes)
        # Head Activation: Softmax(dim=1)

    def forward(self, x):
        # ... forward pass
        return x

# [5] Configuration
model = CNNv16(num_classes=10)  # TODO: Set num_classes to your dataset
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# [6] Optimizer
optimizer = optim.AdamW(model.parameters(), lr=0.001)

# [7] Loss Function
criterion = nn.CrossEntropyLoss()

# [8] Data Augmentation
train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# [9] Training Loop
num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    # ... training loop
    print(f"Epoch {epoch+1}/{num_epochs}")

# [10] Save Model
torch.save(model.state_dict(), 'cnn_v16_trained.pth')
```

---

## 8. API Specification

### 8.1 Model Definition API

Since NeuroScope Phase 1 is **client-side only**, there is no backend API. All model definitions are loaded as static JSON files.

**Model Definition Schema:**

```json
{
  "id": "cnn_v16",
  "name": "CNN v16",
  "family": "CNN",
  "version": "16",
  "description": "16-layer Convolutional Neural Network for image classification",
  "layers": [
    {
      "id": "conv1",
      "type": "conv2d",
      "name": "Conv2d_1",
      "params": { "in_channels": 3, "out_channels": 64, "kernel_size": 3, "padding": 1 },
      "code": "nn.Conv2d(3, 64, kernel_size=3, padding=1)"
    }
  ],
  "head": {
    "type": "linear",
    "activation": "softmax",
    "output_neurons": "num_classes",
    "code": "nn.Linear(in_features, num_classes)",
    "activation_code": "nn.Softmax(dim=1)",
    "description": "Classification head — outputs probability for each class"
  },
  "extensions": [
    {
      "id": "optimizer",
      "name": "Optimizer",
      "category": "training",
      "color": "green",
      "options": [
        {
          "id": "adamw",
          "name": "AdamW",
          "code": "optimizer = optim.AdamW(model.parameters(), lr={lr})",
          "description": "Adam with decoupled weight decay",
          "when_to_use": "Best for most modern architectures",
          "consequences": "Slightly more compute than Adam",
          "default": true
        }
      ]
    }
  ]
}
```

### 8.2 Export API (Client-Side)

Export is handled entirely in the browser using JavaScript libraries:

| Format | Library | Method |
|--------|---------|--------|
| .ipynb | Custom JSON builder | Generate Jupyter Notebook JSON structure |
| .yaml | js-yaml | Serialize model definition to YAML |
| .py | Custom string builder | Generate Python script from code template |

---

## 9. Testing Strategy

### 9.1 Unit Tests

| Component | Test Cases |
|-----------|-----------|
| Model Definition Parser | Load JSON, validate schema, handle missing fields |
| Code Generator | Generate correct Python code for each extension combination |
| Export | .ipynb opens correctly in Jupyter; .yaml is valid |
| Extension Panel | All options render; Apply button works; code updates |

### 9.2 Integration Tests

| Scenario | Expected Behavior |
|----------|-------------------|
| Select CNN v16 → Configure all extensions → Export | Notebook runs without errors on Colab |
| Change optimizer from AdamW to SGD → Code updates | Notebook reflects the change |
| Open Develop Mode → Freeze layer → Export | Frozen layer appears in exported code |
| Export → Import into Colab → Run | Training starts without errors |

### 9.3 Usability Tests

| Test | Metric |
|------|--------|
| First-time user builds a model | Time < 10 minutes |
| User understands what each option does | Quiz score > 80% |
| User can export and run notebook | Success rate > 90% |
| User finds the tool intuitive | SUS score > 70 |

---

## 10. Future Roadmap

### Phase 2 (Aug-Oct 2026)
- YOLO model family (v8, v10, v11) with all sizes
- ResNet model family (18, 34, 50, 101, 152)
- EfficientNet model family (B0-B7)
- Model comparison (side-by-side)
- More extensions per model family

### Phase 3 (Nov 2026 - Jan 2027)
- Multi-modal pipelines (combine models)
- VS Code Extension
- AI Agent Plugins (Claude, Copilot)
- GPU backend for in-browser training

### Phase 4 (Feb 2027+)
- Desktop Application (Windows/Mac)
- Offline mode
- Community model definitions
- Plugin system for custom extensions

---

*Document prepared for DigiNeurons development team.*
*For questions, contact: hazemelerefy@gmail.com*
