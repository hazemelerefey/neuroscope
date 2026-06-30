# NeuroScope — Technical Architecture Document

**Project:** NeuroScope Visual Builder
**Version:** 2.0 (Phase 1 — CNN v16)
**Date:** June 30, 2026
**For:** Software Track (Shahd, Mohamed Wagdi, Ziad, Yossef Safout)

---

## 1. System Architecture

### 1.1 Architecture Overview

NeuroScope is a **full-stack application** with a React frontend and a Python FastAPI backend. The frontend handles 3D visualization and the visual builder UI. The backend serves model definitions, educational content, and generates export artifacts (Jupyter notebooks and YAML configurations).

```
┌──────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  React App   │  │  Three.js    │  │  Notebook / YAML      │  │
│  │  (UI Layer)  │  │  (3D Layer)  │  │  Preview              │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────┘  │
│         │                 │                       │              │
│         └─────────────────┼───────────────────────┘              │
│                           │                                      │
│                    ┌──────┴───────┐                              │
│                    │  Zustand     │                              │
│                    │  Store       │                              │
│                    └──────┬───────┘                              │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │  HTTP (fetch)
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  /api/models │  │ /api/export  │  │  /api/educational     │  │
│  │  Routes      │  │ Routes       │  │  Routes               │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────┘  │
│         │                 │                       │              │
│         └─────────────────┼───────────────────────┘              │
│                           │                                      │
│         ┌─────────────────┼─────────────────────┐               │
│         │                 │                     │               │
│  ┌──────┴───────┐  ┌─────┴──────┐  ┌──────────┴────────────┐  │
│  │  Model       │  │  Export    │  │  Educational           │  │
│  │  Catalog     │  │  Engine    │  │  Content               │  │
│  │  (JSON)      │  │  nbformat  │  │  (JSON)                │  │
│  │              │  │  PyYAML    │  │                        │  │
│  └──────────────┘  └────────────┘  └────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **UI Framework** | React | 18+ | Component-based UI |
| **Language** | TypeScript | 5+ | Type safety |
| **3D Engine** | Three.js | r160+ | WebGL 3D rendering |
| **3D React Wrapper** | React Three Fiber | 8+ | React bindings for Three.js |
| **State Management** | Zustand | 4+ | Lightweight global state |
| **Styling** | Tailwind CSS | 3+ | Utility-first CSS |
| **Build Tool** | Vite | 5+ | Fast development build |
| **Backend Framework** | FastAPI | 0.110+ | Async Python API server |
| **Validation** | Pydantic | 2+ | Request/response models |
| **Notebook Generation** | nbformat | 5+ | Programmatic .ipynb creation |
| **YAML Generation** | PyYAML | 6+ | YAML serialization |
| **Rate Limiting** | slowapi | 0.1+ | API rate limiting |
| **ASGI Server** | uvicorn | 0.29+ | Production ASGI server |

### 1.3 Project Structure

```
neuroscope/
├── frontend/
│   ├── public/
│   │   └── models/                    # Static model definition fallbacks
│   │       └── cnn_v16.json
│   ├── src/
│   │   ├── App.tsx                    # Root component
│   │   ├── main.tsx                   # Entry point
│   │   ├── store.ts                   # Zustand global state
│   │   ├── types.ts                   # TypeScript type definitions
│   │   │
│   │   ├── components/
│   │   │   ├── Canvas3D.tsx           # 3D machine visualization (empty state, core engine, extension orbit)
│   │   │   ├── ModelSelector.tsx      # Tree selector: Family → Version → Size
│   │   │   ├── ExtensionConfig.tsx    # Option cards with educational descriptions
│   │   │   ├── NotebookWindow.tsx     # Live code preview with .ipynb / .yaml tabs
│   │   │   ├── DevelopMode.tsx        # Layer inspector with freeze/unfreeze/remove/add
│   │   │   ├── InfoPanel.tsx          # Model + extension summary bar
│   │   │   ├── ExportButton.tsx       # Export trigger
│   │   │   ├── ExportMenu.tsx         # Format selection (.ipynb / .yaml)
│   │   │   └── shared/
│   │   │       ├── GlowEffect.tsx     # Reusable glow animation
│   │   │       ├── ParticleSystem.tsx  # Background particles
│   │   │       └── Tooltip.tsx        # Educational tooltips
│   │   │
│   │   ├── hooks/
│   │   │   ├── useModelLoader.ts      # Fetch model from backend API
│   │   │   ├── useCodeSync.ts         # Sync state → code preview
│   │   │   └── useExport.ts           # Export via backend API
│   │   │
│   │   └── utils/
│   │       ├── colors.ts              # Category color constants
│   │       ├── animations.ts          # Shared animation configs
│   │       └── formatters.ts          # Code formatting helpers
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── requirements.txt               # Python dependencies
│   │
│   ├── routes/
│   │   ├── models.py                  # /api/models endpoints
│   │   ├── export.py                  # /api/export endpoints
│   │   └── educational.py             # /api/educational endpoints
│   │
│   ├── engine/
│   │   ├── notebook_builder.py        # .ipynb generation with nbformat
│   │   ├── yaml_exporter.py           # YAML generation with PyYAML
│   │   └── template_engine.py         # Code template system
│   │
│   ├── data/
│   │   ├── models/
│   │   │   └── cnn_v16.json           # CNN v16 full definition
│   │   ├── extensions/
│   │   │   ├── optimizer.json
│   │   │   ├── activation.json
│   │   │   ├── loss.json
│   │   │   ├── learning_rate.json
│   │   │   ├── batch_size.json
│   │   │   ├── epochs.json
│   │   │   └── augmentation.json
│   │   └── education/
│   │       ├── head_layer.json
│   │       └── general.json
│   │
│   ├── schemas/
│   │   ├── models.py                  # Pydantic model schemas
│   │   └── export.py                  # Pydantic export request/response schemas
│   │
│   └── rules/
│       └── builder_rules.yaml         # Validation rules for builder configurations
│
├── docker-compose.yml                 # Frontend + Backend orchestration
├── docker/
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── nginx/
│       └── nginx.conf
│
└── docs/
    └── technical/
        └── NeuroScope-Technical-Architecture.md
```

---

## 2. State Management

### 2.1 Global State (Zustand — `store.ts`)

```typescript
interface NeuroScopeState {
  // Model catalog (fetched from backend)
  modelFamilies: ModelFamily[];
  selectedModel: SelectedModel | null;

  // Extensions
  extensions: Extension[];
  activeExtension: string | null;

  // Workspace
  workspaceReady: boolean;

  // UI
  rightPanelOpen: boolean;
  rightPanelContent: 'models' | 'extension-config' | null;
  notebookOpen: boolean;
  developModeOpen: boolean;

  // Code preview
  notebookCells: NotebookCell[];
  yamlPreview: string;

  // Actions
  loadModelFamilies: () => Promise<void>;
  selectModel: (family: string, version: string, size?: string) => Promise<void>;
  configureExtension: (extensionId: string, optionId: string) => void;
  openExtensionPanel: (extensionId: string) => void;
  closeExtensionPanel: () => void;
  toggleNotebook: () => void;
  toggleDevelopMode: () => void;
  exportNotebook: () => Promise<void>;
  exportYaml: () => Promise<void>;
  resetWorkspace: () => void;
}
```

### 2.2 State Flow

```
User Action → Zustand Action → State Update → React Re-render
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            Canvas3D update   NotebookWindow   InfoPanel update
                              code preview
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            POST /api/export/notebook       POST /api/export/yaml
                    │                               │
                    ▼                               ▼
              .ipynb download                  .yaml download
```

---

## 3. Component Specifications

### 3.1 Canvas3D Component

**File:** `components/Canvas3D.tsx`

**Responsibilities:**
- Render the 3D machine visualization (React Three Fiber)
- Show empty state with centered + button when no model is selected
- Render core engine block when a model is active
- Orbit extension octahedra around the core engine
- Draw cables connecting extensions to the core engine
- Visualize model size via core engine scale/detail

**3D Specifications:**
- **Core engine block:** BoxGeometry with metallic material, circuit-line shader, PointLight glow
- **Extension octahedra:** OctahedronGeometry with category-color emissive borders
- **Cables:** CatmullRomCurve3 → TubeGeometry connecting each extension to the core
- **Size visualization:** Core engine scale grows with model parameter count; surface detail (bumps, ridges) increases with layer count
- **Empty state:** Floating particles + centered "+" button with glow

**Key Behavior:**
- When empty: Show `ParticleSystem` + `PlusButton` centered
- When model selected: Show `CoreEngine` + `ExtensionBlock` octahedra orbiting
- Camera: OrbitControls with limits (no flip, min/max distance)

### 3.2 ModelSelector Component

**File:** `components/ModelSelector.tsx`

**Responsibilities:**
- Tree-based model selector: **Family → Version → Size**
- Fetch available families from `GET /api/models`
- On family/version selection, fetch full definition from `GET /api/models/{family}/{version}`
- Present size variants (e.g., Small, Medium, Large) when applicable
- Update Zustand store on selection

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back            Model Selector   │
│                                     │
│  🧠 CNN                             │
│    ├── v16                           │
│    │   ├── Small  (5 layers)        │
│    │   ├── Medium (8 layers)  ✓     │
│    │   └── Large  (12 layers)       │
│    └── v18                           │
│        └── ...                       │
│                                     │
│  🔄 Transformer                      │
│    └── (coming soon)                 │
│                                     │
└─────────────────────────────────────┘
```

### 3.3 ExtensionConfig Component

**File:** `components/ExtensionConfig.tsx`

**Responsibilities:**
- Display option cards for the selected extension (optimizer, loss, etc.)
- Each card shows: name, description, when-to-use guidance, and consequence warnings
- Radio-button selection with Apply button
- Educational descriptions embedded in each option

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back            Extension Config │
│                                     │
│  ⚡ OPTIMIZER                       │
│                                     │
│  ○ SGD                              │
│    Stochastic Gradient Descent...   │
│                                     │
│  ● AdamW              [SELECTED]    │
│    Adam with decoupled weight...    │
│    When to use: Best for most...    │
│    ⚠ If wrong: Slightly higher...   │
│                                     │
│  ○ Adam                             │
│    Adaptive learning rate...        │
│                                     │
│  ○ RMSprop                          │
│    Adaptive learning rate...        │
│                                     │
│           [Apply]                   │
└─────────────────────────────────────┘
```

### 3.4 NotebookWindow Component

**File:** `components/NotebookWindow.tsx`

**Responsibilities:**
- Collapsible window in top-right corner
- **Tabbed view:** `.ipynb` (Python code cells) and `.yaml` (model configuration)
- Auto-opens on model selection and extension changes
- Syntax-highlighted code display
- Live preview updates as builder state changes

**States:**
- **Collapsed:** Small tab showing "📓 Notebook"
- **Expanded:** Full window with `.ipynb` / `.yaml` tab toggle and syntax-highlighted content

**Auto-open triggers:**
- Model selected
- Extension configured or changed
- Develop mode changes (freeze/unfreeze/remove/add layers)

### 3.5 DevelopMode Component

**File:** `components/DevelopMode.tsx`

**Responsibilities:**
- Layer inspector view showing all model layers in a scrollable list
- **Freeze / Unfreeze** individual layers (toggles `requires_grad`)
- **Remove** layers from the model architecture
- **Add** new layers from a palette (conv, batchnorm, activation, dropout, pooling)
- Changes propagate to the notebook/YAML preview in real time

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  ← Back              Develop Mode — Layer Inspector     │
│                                                         │
│  #  │ Layer            │ Type     │ Actions             │
│  ───┼──────────────────┼──────────┼────────────────────│
│  1  │ conv1            │ Conv2D   │ 🔒 Freeze │ ✕ Remove│
│  2  │ bn1              │ BatchNorm│ 🔒 Freeze │ ✕ Remove│
│  3  │ relu1            │ ReLU     │ 🔒 Freeze │ ✕ Remove│
│  4  │ pool1            │ MaxPool  │ 🔒 Freeze │ ✕ Remove│
│  ...│                  │          │                      │
│                                                         │
│  [+ Add Layer]   [Conv2D] [BatchNorm] [ReLU] [Dropout] │
└─────────────────────────────────────────────────────────┘
```

### 3.6 InfoPanel Component

**File:** `components/InfoPanel.tsx`

**Responsibilities:**
- Display model + extension summary (always visible at bottom)
- Shows model name, head layer, configured optimizer, LR, batch size, epochs
- Updates live when extensions are configured

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ 🧠 CNN v16 | 🎯 Head: Softmax (10 classes) | ⚡ AdamW  │
│ 📈 LR: 0.001 | 📦 Batch: 16 | 🔄 Epochs: 100         │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Backend API

### 4.1 API Overview

The FastAPI backend serves model data, educational content, and handles export generation. All endpoints return JSON. Export endpoints accept a builder configuration and return generated artifacts.

**Base URL:** `http://localhost:8000`

### 4.2 Endpoints

#### `GET /api/models`

List all available model families with their versions.

**Response:**
```json
{
  "families": [
    {
      "id": "cnn",
      "name": "CNN",
      "description": "Convolutional Neural Networks",
      "versions": [
        { "version": "16", "name": "CNN v16", "sizes": ["small", "medium", "large"] }
      ]
    }
  ]
}
```

#### `GET /api/models/{family}/{version}`

Full model definition including layers, extensions, head, and educational content.

**Response:** Full `ModelDefinition` JSON (see §6.1 for schema).

#### `POST /api/export/notebook`

Generate a Jupyter notebook from a builder configuration.

**Request body:**
```json
{
  "model": { "family": "cnn", "version": "16", "size": "medium" },
  "extensions": {
    "optimizer": "adamw",
    "loss": "cross_entropy",
    "learning_rate": 0.001,
    "batch_size": 16,
    "epochs": 100,
    "augmentation": ["random_flip", "normalize"]
  },
  "frozen_layers": ["bn1", "bn2"],
  "removed_layers": [],
  "added_layers": []
}
```

**Response:** `.ipynb` JSON (nbformat 4.5 compliant) — downloaded as a file.

#### `POST /api/export/yaml`

Generate a model YAML configuration from a builder configuration.

**Request body:** Same as `/api/export/notebook`.

**Response:** YAML string — downloaded as a `.yaml` file.

#### `GET /api/educational/{topic}`

Retrieve educational content for a given topic.

**Path parameter:** `topic` — one of `head_layer`, `general`, or an extension ID (e.g., `optimizer`, `loss`).

**Response:**
```json
{
  "topic": "optimizer",
  "title": "Optimizers",
  "sections": [
    {
      "heading": "What is an Optimizer?",
      "content": "An optimizer adjusts model parameters to minimize the loss function..."
    }
  ]
}
```

### 4.3 Rate Limiting

All endpoints are rate-limited via `slowapi`:
- **GET endpoints:** 60 requests/minute per IP
- **POST /api/export/*:** 10 requests/minute per IP

---

## 5. Data Flow

### 5.1 Visual Builder → Export Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  ModelSelector  │────▶│  Zustand Store  │────▶│  Canvas3D        │
│  (pick model)   │     │  (selectedModel)│     │  (3D render)     │
└─────────────────┘     └────────┬────────┘     └──────────────────┘
                                 │
┌─────────────────┐              │              ┌──────────────────┐
│  ExtensionConfig│──────────────┼─────────────▶│  InfoPanel       │
│  (pick options) │              │              │  (summary bar)   │
└─────────────────┘              │              └──────────────────┘
                                 │
┌─────────────────┐              │              ┌──────────────────┐
│  DevelopMode    │──────────────┼─────────────▶│  NotebookWindow  │
│  (edit layers)  │              │              │  (live preview)  │
└─────────────────┘              │              └──────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Export Button         │
                    │  POST /api/export/...  │
                    └───────────┬────────────┘
                                │
                    ┌───────────┴────────────┐
                    ▼                        ▼
              .ipynb download          .yaml download
```

### 5.2 Model Loading Flow

```
App Mount
    │
    ▼
GET /api/models  →  Populate ModelSelector tree
    │
    ▼
User selects Family + Version + Size
    │
    ▼
GET /api/models/{family}/{version}  →  Full ModelDefinition
    │
    ▼
Zustand store updated:
  - selectedModel
  - extensions (with defaults)
  - notebookCells (generated)
  - yamlPreview (generated)
    │
    ▼
Canvas3D renders core engine + extension octahedra
NotebookWindow auto-opens with preview
InfoPanel updates with model summary
```

---

## 6. 3D Rendering Specifications

### 6.1 Scene Setup

```typescript
scene.background = new THREE.Color(0x000000);
scene.fog = new THREE.FogExp2(0x000000, 0.05);

camera.position = [0, 5, 10];
camera.fov = 45;

ambientLight = new THREE.AmbientLight(0x111111);
directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
pointLight = new THREE.PointLight(0x00d4ff, 1, 50); // Blue core glow

renderer.antialias = true;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
```

### 6.2 Core Engine Block

- **Geometry:** BoxGeometry — base size 2×2×2 units
- **Material:** MeshStandardMaterial with metallic surface, custom circuit-line shader
- **Glow:** PointLight (blue, `#00d4ff`) + emissive material
- **Size visualization:** Scale grows with parameter count; each layer group adds 0.3 units of surface detail (bumps, ridges)
- **Label:** HTML overlay showing model name

### 6.3 Extension Octahedra

- **Geometry:** OctahedronGeometry (radius ~0.6 units)
- **Material:** MeshStandardMaterial with category-color emissive border
- **Position:** Orbital arrangement around the core engine (angle calculated from extension index / total count)
- **States:**
  - *Unconfigured:* Dark material, dim cable
  - *Configured:* Glowing material, illuminated cable, subtle pulse animation

### 6.4 Cable Rendering

```typescript
const curve = new THREE.CatmullRomCurve3([
  extensionPosition,
  controlPoint1,
  controlPoint2,
  coreEnginePosition
]);
const tubeGeometry = new THREE.TubeGeometry(curve, 64, 0.05, 8, false);
const tubeMaterial = new THREE.MeshStandardMaterial({
  color: categoryColor,
  emissive: isConfigured ? categoryColor : 0x333333,
  emissiveIntensity: isConfigured ? 0.5 : 0.1
});
```

### 6.5 Particle System

- 200 particles floating slowly around the scene
- Color: White, low opacity (0.3)
- Movement: Gentle drift (0.01 units/frame)
- When model is active: Particles clear away from center (radius = 5 units)

### 6.6 Post-Processing Bloom

```typescript
<EffectComposer>
  <Bloom
    luminanceThreshold={0.6}
    luminanceSmoothing={0.9}
    intensity={0.5}
  />
</EffectComposer>
```

### 6.7 Animation Specifications

| Animation | Duration | Easing | Trigger |
|-----------|----------|--------|---------|
| Power On | 1.5s | ease-out | Model selected |
| Extension Glow | 0.8s | ease-in-out | Extension configured |
| Cable Illuminate | 0.5s | ease-in | Extension configured |
| Panel Slide In | 0.3s | ease-out | Extension clicked |
| Panel Slide Out | 0.2s | ease-in | Back button clicked |
| Notebook Open | 0.3s | ease-out | Auto-trigger |
| Notebook Close | 0.2s | ease-in | Manual close |

---

## 7. Model Definition Format

### 7.1 Type Definitions (`types.ts`)

```typescript
interface ModelFamily {
  id: string;
  name: string;
  description: string;
  versions: ModelVersion[];
}

interface ModelVersion {
  version: string;
  name: string;
  sizes: string[] | null;
}

interface SelectedModel {
  family: string;
  version: string;
  size: string | null;
  definition: ModelDefinition;
}

interface ModelDefinition {
  id: string;
  name: string;
  family: string;
  version: string;
  description: string;
  sizes: string[] | null;
  layers: LayerDefinition[];
  head: HeadDefinition;
  extensions: ExtensionDefinition[];
  educational: EducationalContent;
}

interface LayerDefinition {
  id: string;
  type: string;
  name: string;
  params: Record<string, any>;
  code: string;
  freezable: boolean;
}

interface HeadDefinition {
  type: string;
  activation: string;
  output_neurons: string;
  code: string;
  activation_code: string;
  description: string;
}

interface Extension {
  id: string;
  name: string;
  category: 'training' | 'data' | 'functional' | 'core';
  color: string;
  icon: string;
  selectedOption: string | null;
  options: ExtensionOption[];
}

interface ExtensionDefinition {
  id: string;
  name: string;
  category: 'training' | 'data' | 'functional' | 'core';
  color: string;
  icon: string;
  options: ExtensionOption[];
}

interface ExtensionOption {
  id: string;
  name: string;
  code: string;
  description: string;
  when_to_use: string;
  consequences: string;
  default: boolean;
}
```

### 7.2 CNN v16 Definition Structure

```json
{
  "id": "cnn_v16",
  "name": "CNN v16",
  "family": "CNN",
  "version": "16",
  "description": "A 16-layer convolutional neural network for image classification.",
  "sizes": ["small", "medium", "large"],
  "layers": [
    {
      "id": "conv1",
      "type": "conv2d",
      "name": "Conv Block 1",
      "params": { "in_channels": 3, "out_channels": 64, "kernel_size": 3, "padding": 1 },
      "code": "nn.Conv2d(3, 64, kernel_size=3, padding=1)",
      "freezable": true
    },
    {
      "id": "bn1",
      "type": "batchnorm",
      "name": "BatchNorm 1",
      "params": { "num_features": 64 },
      "code": "nn.BatchNorm2d(64)",
      "freezable": true
    }
  ],
  "head": {
    "type": "linear",
    "activation": "softmax",
    "output_neurons": "num_classes",
    "code": "nn.Linear(in_features, num_classes)",
    "activation_code": "nn.Softmax(dim=1)",
    "description": "Classification head with softmax activation"
  },
  "extensions": [ /* ExtensionDefinition[] */ ],
  "educational": {
    "overview": "CNN v16 is designed for...",
    "layers_guide": "Each conv block consists of...",
    "tips": ["Start with medium size", "Use AdamW optimizer"]
  }
}
```

---

## 8. Builder Rules

### 8.1 Validation Rules (`builder_rules.yaml`)

The backend validates builder configurations against a set of rules before generating exports. Rules produce **warnings** (non-blocking) or **errors** (blocking).

```yaml
rules:
  # Activation warnings
  - id: sigmoid_in_deep_net
    condition: "activation == 'sigmoid' AND num_layers > 8"
    severity: warning
    message: "Sigmoid in deep networks can cause vanishing gradients. Consider ReLU or SiLU."

  - id: softmax_middle_layers
    condition: "activation == 'softmax' AND layer_position != 'head'"
    severity: error
    message: "Softmax should only be used in the output head layer."

  # Batch normalization
  - id: missing_batchnorm
    condition: "has_conv_layers == true AND has_batchnorm == false"
    severity: warning
    message: "Convolutional layers without batch normalization may train slowly or diverge."

  # Learning rate
  - id: high_learning_rate
    condition: "learning_rate > 0.01"
    severity: warning
    message: "Learning rate above 0.01 may cause training instability."

  - id: very_high_learning_rate
    condition: "learning_rate > 0.1"
    severity: error
    message: "Learning rate above 0.1 will almost certainly diverge."

  # Optimizer + loss compatibility
  - id: sgd_no_momentum
    condition: "optimizer == 'sgd' AND momentum == null"
    severity: warning
    message: "SGD without momentum is very slow. Consider adding momentum=0.9."

  # Batch size
  - id: very_small_batch
    condition: "batch_size < 4"
    severity: warning
    message: "Very small batch sizes cause noisy gradients. Consider >= 8."

  # Frozen layers
  - id: frozen_output_layer
    condition: "frozen_layers contains head_layer"
    severity: error
    message: "Cannot freeze the output head layer — it must be trainable."
```

### 8.2 Rule Evaluation

Rules are evaluated server-side in `POST /api/export/*` endpoints. Warnings are returned in the response alongside the generated artifact:

```json
{
  "notebook": { /* .ipynb JSON */ },
  "warnings": [
    {
      "rule_id": "sigmoid_in_deep_net",
      "message": "Sigmoid in deep networks can cause vanishing gradients. Consider ReLU or SiLU.",
      "severity": "warning"
    }
  ]
}
```

---

## 9. Export Formats

### 9.1 Jupyter Notebook (.ipynb)

Generated by `backend/engine/notebook_builder.py` using `nbformat`.

```json
{
  "nbformat": 4,
  "nbformat_minor": 5,
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "name": "python",
      "version": "3.10.0"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "source": ["# NeuroScope — CNN v16 Training Notebook\n", "Generated by NeuroScope Visual Builder\n"],
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": ["import torch\n", "import torch.nn as\n", "import torch.optim as optim\n"],
      "metadata": {},
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": ["## Model Definition\n"],
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": ["class CNNv16(nn.Module):\n", "    def __init__(self, num_classes=10):\n", "        ...\n"],
      "metadata": {},
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "markdown",
      "source": ["## Training Configuration\n"],
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": ["optimizer = optim.AdamW(model.parameters(), lr=0.001)\n", "criterion = nn.CrossEntropyLoss()\n"],
      "metadata": {},
      "execution_count": null,
      "outputs": []
    }
  ]
}
```

**Structure:**
1. Title markdown cell (model name, generation date, NeuroScope branding)
2. Environment setup code cell (imports)
3. Model definition code cell (class with all layers, respecting frozen/removed/added)
4. Configuration code cell (optimizer, loss, LR, batch size, epochs)
5. Data augmentation code cell (transforms)
6. Training loop code cell
7. Save model code cell

### 9.2 Model YAML

Generated by `backend/engine/yaml_exporter.py` using PyYAML.

```yaml
# NeuroScope — CNN v16 Configuration
# Generated by NeuroScope Visual Builder

model:
  name: CNNv16
  family: CNN
  version: 16
  size: medium
  layers:
    - id: conv1
      type: conv2d
      params: { in_channels: 3, out_channels: 64, kernel_size: 3, padding: 1 }
    - id: bn1
      type: batchnorm
      params: { num_features: 64 }
    - id: relu1
      type: activation
      params: { function: relu }
    # ... remaining layers
  head:
    type: linear
    activation: softmax
    output_neurons: num_classes

training:
  optimizer: AdamW
  optimizer_params: { weight_decay: 0.01 }
  lr: 0.001
  loss: CrossEntropyLoss
  batch_size: 16
  epochs: 100

augmentation:
  - RandomHorizontalFlip(p=0.5)
  - ToTensor()
  - Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

builder_state:
  frozen_layers:
    - bn1
    - bn2
  removed_layers: []
  added_layers: []
```

---

## 10. Deployment

### 10.1 Development

```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 10.2 Docker Compose

```yaml
version: "3.9"

services:
  frontend:
    build:
      context: .
      dockerfile: docker/frontend.Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build:
      context: .
      dockerfile: docker/backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=http://localhost:3000
      - LOG_LEVEL=info
    volumes:
      - ./backend/data:/app/data   # Model definitions + educational content
```

### 10.3 Environment Variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `CORS_ORIGINS` | Backend | `*` | Comma-separated allowed origins |
| `LOG_LEVEL` | Backend | `info` | Logging level (debug/info/warning/error) |
| `RATE_LIMIT_ENABLED` | Backend | `true` | Enable/disable rate limiting |
| `VITE_API_URL` | Frontend | `http://localhost:8000` | Backend API base URL |

### 10.4 Production Build

```bash
# Frontend
cd frontend
npm run build
# Output: frontend/dist/

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 10.5 Deployment Options

| Option | Frontend | Backend | Notes |
|--------|----------|---------|-------|
| Docker Compose | nginx container | uvicorn container | Recommended for production |
| Vercel + Railway | Vercel (static) | Railway (FastAPI) | Managed hosting |
| Netlify + Render | Netlify (static) | Render (FastAPI) | Free tier available |

---

## 11. Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial load | < 3s | Lighthouse |
| 3D FPS | ≥ 30 | Chrome DevTools |
| Extension click → panel | < 500ms | User perception |
| API model list | < 200ms | Network tab |
| API export | < 2s | Network tab |
| Memory usage | < 200MB | Chrome Task Manager |

### Optimization Strategies

| Strategy | Implementation |
|----------|---------------|
| Lazy load 3D assets | React.lazy + Suspense |
| Instance reuse | Shared geometries and materials |
| LOD (Level of Detail) | Simpler geometry when zoomed out |
| Debounce code preview | 100ms debounce on state changes |
| Memoize expensive computations | useMemo for code generation |
| Backend caching | Model definitions cached in memory |
| Gzip responses | FastAPI middleware for compressed responses |

---

## 12. Testing Strategy

### 12.1 Frontend Unit Tests (Vitest)

| Component | Test |
|-----------|------|
| store.ts | State actions update correctly |
| ModelSelector | Renders tree; selection triggers fetch |
| ExtensionConfig | Renders options; Apply button works |
| InfoPanel | Updates when extensions change |
| NotebookWindow | Tab switching; content rendering |

### 12.2 Backend Unit Tests (pytest)

| Module | Test |
|--------|------|
| routes/models.py | Returns correct family list and model definitions |
| routes/export.py | Generates valid .ipynb and .yaml |
| routes/educational.py | Returns content for each topic |
| engine/notebook_builder.py | Produces nbformat-compliant output |
| engine/yaml_exporter.py | Produces valid YAML |
| rules/builder_rules.py | Catches all defined rule violations |

### 12.3 Integration Tests

| Scenario | Test |
|----------|------|
| Full flow | Select model → configure extensions → export notebook → validate .ipynb |
| Change flow | Change optimizer → preview updates → export reflects change |
| Develop mode | Open → freeze layer → export shows frozen layer |
| Builder rules | Configure sigmoid + deep net → receive warning |

### 12.4 E2E Tests (Playwright)

| Scenario | Test |
|----------|------|
| Complete journey | Load app → select model → configure all extensions → develop mode → export both formats |
| API error handling | Backend down → frontend shows graceful error |
| Mobile responsive | Verify layout on tablet viewport |

---

## 13. Development Guidelines

### 13.1 Code Style

- **TypeScript:** Strict mode enabled
- **Components:** Functional components with hooks
- **State:** Zustand for global; useState for local
- **Styling:** Tailwind CSS; no inline styles
- **3D:** React Three Fiber; declarative, not imperative
- **Python:** PEP 8; type hints on all functions
- **API:** Pydantic models for all request/response schemas

### 13.2 Git Workflow

```
main
  └── develop
       ├── feature/canvas-3d
       ├── feature/model-selector
       ├── feature/extensions
       ├── feature/notebook-preview
       ├── feature/develop-mode
       ├── feature/backend-api
       └── feature/export-engine
```

### 13.3 PR Requirements

- [ ] TypeScript compiles without errors
- [ ] Python type checks pass (mypy)
- [ ] All tests pass (frontend + backend)
- [ ] Screenshot/recording of visual changes
- [ ] No console errors
- [ ] API endpoints return correct status codes

---

*Document prepared for DigiNeurons Software Track.*
*For questions, contact: hazemelerefy@gmail.com*
