# NeuroScope — Technical Architecture Document

**Project:** NeuroScope Visual Builder
**Version:** 1.0 (Phase 1 — CNN v16)
**Date:** June 29, 2026
**For:** Software Track (Shahd, Mohamed Wagdi, Ziad, Yossef Safout)

---

## 1. System Architecture

### 1.1 Architecture Overview

NeuroScope Phase 1 is a **client-side only** application. There is no backend server. All 3D rendering, code generation, and export happen in the browser.

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER                               │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  React App   │  │  Three.js    │  │  Code Gen    │  │
│  │  (UI Layer)  │  │  (3D Layer)  │  │  Engine      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│                    ┌──────┴───────┐                     │
│                    │  State Mgmt  │                     │
│                    │  (Zustand)   │                     │
│                    └──────────────┘                     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Static Assets                        │  │
│  │  - Model definitions (JSON)                      │  │
│  │  - Educational content (JSON)                    │  │
│  │  - 3D assets (textures, models)                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
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
| **Export** | js-yaml, custom ipynb builder | — | File export |

### 1.3 Project Structure

```
frontend/
├── public/
│   └── models/                    # Model definition JSON files
│       └── cnn_v16.json
├── src/
│   ├── App.tsx                    # Root component
│   ├── main.tsx                   # Entry point
│   ├── store.ts                   # Zustand global state
│   ├── types.ts                   # TypeScript type definitions
│   │
│   ├── components/
│   │   ├── workspace/
│   │   │   ├── Workspace.tsx      # Main 3D canvas area
│   │   │   ├── PlusButton.tsx     # Central + button
│   │   │   └── EmptyState.tsx     # Empty workspace state
│   │   │
│   │   ├── engine/
│   │   │   ├── CoreEngine.tsx     # 3D core engine block
│   │   │   ├── EngineContextMenu.tsx  # Right-click menu
│   │   │   └── HeadLayer.tsx      # Head layer display
│   │   │
│   │   ├── extensions/
│   │   │   ├── ExtensionBlock.tsx  # 3D extension satellite
│   │   │   ├── ExtensionCable.tsx  # Cable connecting to engine
│   │   │   ├── ExtensionPanel.tsx  # Right-side config panel
│   │   │   └── OptionCard.tsx     # Individual option in panel
│   │   │
│   │   ├── info/
│   │   │   ├── InfoPanel.tsx      # Bottom info bar
│   │   │   └── InfoItem.tsx       # Individual info point
│   │   │
│   │   ├── notebook/
│   │   │   ├── NotebookWindow.tsx  # Collapsible code viewer
│   │   │   ├── CodeBlock.tsx       # Syntax-highlighted code
│   │   │   └── MarkdownBlock.tsx   # Markdown comments
│   │   │
│   │   ├── model-selector/
│   │   │   ├── ModelMenu.tsx      # Model selection menu
│   │   │   ├── ModelCard.tsx      # Individual model card
│   │   │   └── RightPanel.tsx     # Collapsible right panel
│   │   │
│   │   ├── develop/
│   │   │   ├── DevelopMode.tsx    # Layer editor view
│   │   │   ├── LayerItem.tsx      # Individual layer row
│   │   │   └── LayerControls.tsx  # Freeze/unfreeze/remove
│   │   │
│   │   ├── export/
│   │   │   ├── ExportButton.tsx   # Export trigger
│   │   │   └── ExportMenu.tsx     # Format selection
│   │   │
│   │   └── shared/
│   │       ├── GlowEffect.tsx     # Reusable glow animation
│   │       ├── ParticleSystem.tsx  # Background particles
│   │       └── Tooltip.tsx        # Educational tooltips
│   │
│   ├── engine/
│   │   ├── codeGenerator.ts       # Code generation logic
│   │   ├── notebookBuilder.ts     # .ipynb JSON builder
│   │   ├── yamlExporter.ts        # YAML export
│   │   └── templateEngine.ts      # Code template system
│   │
│   ├── data/
│   │   ├── models/
│   │   │   └── cnn_v16.json       # CNN v16 definition
│   │   ├── extensions/
│   │   │   ├── optimizer.json     # Optimizer options + education
│   │   │   ├── activation.json    # Activation options + education
│   │   │   ├── loss.json          # Loss options + education
│   │   │   ├── learning_rate.json # LR options + education
│   │   │   ├── batch_size.json    # Batch size options + education
│   │   │   ├── epochs.json        # Epochs options + education
│   │   │   └── augmentation.json  # Augmentation options + education
│   │   └── education/
│   │       ├── head_layer.json    # Head layer explanation
│   │       └── general.json       # General DL concepts
│   │
│   ├── hooks/
│   │   ├── useModelLoader.ts      # Load model definition
│   │   ├── useCodeSync.ts         # Sync state → code
│   │   └── useExport.ts           # Export functionality
│   │
│   └── utils/
│       ├── colors.ts              # Category color constants
│       ├── animations.ts          # Shared animation configs
│       └── formatters.ts          # Code formatting helpers
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 2. State Management

### 2.1 Global State (Zustand)

```typescript
interface NeuroScopeState {
  // Model
  selectedModel: ModelDefinition | null;
  isModelActive: boolean;

  // Extensions
  extensions: ExtensionState[];
  activeExtension: string | null;

  // UI
  rightPanelOpen: boolean;
  rightPanelContent: 'models' | 'extension-config' | null;
  notebookOpen: boolean;
  developModeOpen: boolean;
  contextMenuOpen: boolean;
  contextMenuPosition: { x: number; y: number };

  // Code
  generatedCode: string;
  notebookCells: NotebookCell[];

  // Info
  infoItems: InfoItem[];

  // Actions
  selectModel: (modelId: string) => void;
  configureExtension: (extensionId: string, optionId: string) => void;
  openExtensionPanel: (extensionId: string) => void;
  closeExtensionPanel: () => void;
  toggleNotebook: () => void;
  toggleDevelopMode: () => void;
  exportNotebook: () => void;
  exportYaml: () => void;
  resetWorkspace: () => void;
}
```

### 2.2 State Flow

```
User Action → Zustand Action → State Update → React Re-render
                                    ↓
                              Code Generator → Notebook Update
                                    ↓
                              Info Panel Update
```

---

## 3. Component Specifications

### 3.1 Workspace Component

**File:** `components/workspace/Workspace.tsx`

**Responsibilities:**
- Render the 3D canvas (React Three Fiber)
- Handle drag-and-drop from right panel
- Show empty state with + button when no model is selected
- Manage camera controls (orbit, zoom, pan)

**Props:** None (reads from Zustand store)

**Key Behavior:**
- When empty: Show `PlusButton` centered
- When model selected: Show `CoreEngine` + `ExtensionBlock`s
- Camera: OrbitControls with limits (no flip, min/max distance)

### 3.2 CoreEngine Component

**File:** `components/engine/CoreEngine.tsx`

**Responsibilities:**
- Render the 3D core engine block
- Power-on animation when model is selected
- Display model name/label
- Handle click → context menu
- Show head layer info

**3D Specifications:**
- Base: BoxGeometry with metallic material
- Surface: Custom shader for circuit lines
- Glow: PointLight + emissive material
- Label: HTML overlay or TextGeometry
- Animation: Scale from 0 → 1, opacity fade in, glow pulse

**Size Complexity:**
- Base size: 2x2x2 units
- Each layer group adds 0.3 units to surface detail
- More layers = more surface geometry (bumps, ridges)

### 3.3 ExtensionBlock Component

**File:** `components/extensions/ExtensionBlock.tsx`

**Responsibilities:**
- Render a 3D satellite block
- Show category color border
- Glow animation when configured
- Handle click → open extension panel

**3D Specifications:**
- Geometry: BoxGeometry (1x1x1 units)
- Material: MeshStandardMaterial with category color emissive
- Position: Orbit around core engine (calculated based on extension count)
- Cable: THREE.Line or THREE.TubeGeometry connecting to core engine

**States:**
- Unconfigured: Dark material, dim cable
- Configured: Glowing material, illuminated cable, subtle pulse animation

### 3.4 ExtensionPanel Component

**File:** `components/extensions/ExtensionPanel.tsx`

**Responsibilities:**
- Slide in from the right when extension is clicked
- Show all available options with radio buttons
- Show educational content for each option
- Apply button → inject code, update state

**Layout:**
```
┌─────────────────────────────┐
│  ← Back          Extension  │
│                             │
│  ⚡ OPTIMIZER               │
│                             │
│  ○ SGD                      │
│    Stochastic Gradient...   │
│                             │
│  ● AdamW          [SELECTED]│
│    Adam with decoupled...   │
│    When to use: Best for... │
│    ⚠ If wrong: Slightly...  │
│                             │
│  ○ Adam                     │
│    Adaptive learning...     │
│                             │
│  ○ RMSprop                  │
│    Adaptive learning...     │
│                             │
│         [Apply]             │
└─────────────────────────────┘
```

### 3.5 InfoPanel Component

**File:** `components/info/InfoPanel.tsx`

**Responsibilities:**
- Display model details (always visible at bottom)
- Show head layer info
- Update when extensions are configured
- Point-form display

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ 🧠 CNN v16 | 🎯 Head: Softmax (10 classes) | ⚡ AdamW  │
│ 📈 LR: 0.001 | 📦 Batch: 16 | 🔄 Epochs: 100         │
└─────────────────────────────────────────────────────────┘
```

### 3.6 NotebookWindow Component

**File:** `components/notebook/NotebookWindow.tsx`

**Responsibilities:**
- Collapsible window in top-right
- Auto-open on model selection and extension changes
- Syntax-highlighted code display
- Editable code
- Markdown comments between code blocks

**States:**
- Collapsed: Small tab showing "📓 Notebook"
- Expanded: Full window with code blocks

**Auto-open triggers:**
- Model selected
- Extension configured
- Extension changed
- Develop mode changes

---

## 4. 3D Rendering Specifications

### 4.1 Scene Setup

```typescript
// Scene
scene.background = new THREE.Color(0x000000);
scene.fog = new THREE.FogExp2(0x000000, 0.05);

// Camera
camera.position = [0, 5, 10];
camera.fov = 45;

// Lights
ambientLight = new THREE.AmbientLight(0x111111);
directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
pointLight = new THREE.PointLight(0x00d4ff, 1, 50); // Blue core glow

// Renderer
renderer.antialias = true;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
```

### 4.2 Particle System

- 200 particles floating slowly around the scene
- Color: White, low opacity (0.3)
- Movement: Gentle drift (0.01 units/frame)
- When model is active: Particles clear away from center (radius = 5 units)

### 4.3 Cable Rendering

```typescript
// Cable from extension to core engine
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

### 4.4 Glow Effect

```typescript
// Post-processing bloom effect
import { EffectComposer, Bloom } from '@react-three/postprocessing';

<EffectComposer>
  <Bloom
    luminanceThreshold={0.6}
    luminanceSmoothing={0.9}
    intensity={0.5}
  />
</EffectComposer>
```

### 4.5 Animation Specifications

| Animation | Duration | Easing | Trigger |
|-----------|----------|--------|---------|
| Power On | 1.5s | ease-out | Model selected |
| Extension Glow | 0.8s | ease-in-out | Extension configured |
| Cable Illuminate | 0.5s | ease-in | Extension configured |
| Panel Slide In | 0.3s | ease-out | Extension clicked |
| Panel Slide Out | 0.2s | ease-in | Back button clicked |
| Notebook Open | 0.3s | ease-out | Auto-trigger |
| Notebook Close | 0.2s | ease-in | Manual close |
| Context Menu | 0.15s | ease-out | Core engine clicked |

---

## 5. Code Generation Engine

### 5.1 Architecture

```
State (Zustand)
    ↓
CodeGenerator.generate(state)
    ↓
Template Engine
    ├── Load template for selected model
    ├── Inject extension configurations
    ├── Format code with proper indentation
    └── Add markdown comments
    ↓
Output: Python code string
    ↓
NotebookBuilder.build(code)
    ↓
Output: .ipynb JSON structure
```

### 5.2 Template System

Each model has a code template:

```python
# Template: CNN v16
# ============================================
# NeuroScope — {model_name} Training Notebook
# Generated by NeuroScope Visual Builder
# Date: {generated_date}
# ============================================

# [1] Environment Setup
{environment_setup}

# [2] Dataset Import
{dataset_import}

# [3] Imports
{imports}

# [4] Model Definition
{model_definition}

# [5] Configuration
{configuration}

# [6] Optimizer
{optimizer}

# [7] Loss Function
{loss_function}

# [8] Data Augmentation
{augmentation}

# [9] Training Loop
{training_loop}

# [10] Save Model
{save_model}
```

### 5.3 Code Injection Points

Each extension maps to a template placeholder:

| Extension | Placeholder | Code Snippet |
|-----------|-------------|--------------|
| Optimizer | `{optimizer}` | `optimizer = optim.AdamW(model.parameters(), lr={lr})` |
| Activation | `{activation}` | `activation = nn.SiLU()` |
| Loss | `{loss_function}` | `criterion = nn.CrossEntropyLoss()` |
| Learning Rate | `{lr}` | `lr0 = 0.001` |
| Batch Size | `{batch}` | `batch_size = 16` |
| Epochs | `{epochs}` | `num_epochs = 100` |
| Augmentation | `{augmentation}` | `train_transform = transforms.Compose([...])` |

### 5.4 Export Formats

#### Jupyter Notebook (.ipynb)

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
      "source": ["# NeuroScope — CNN v16 Training Notebook\n", ...],
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": ["import torch\n", ...],
      "metadata": {},
      "execution_count": null,
      "outputs": []
    }
  ]
}
```

#### Model YAML

```yaml
model:
  name: CNNv16
  family: CNN
  version: 16
  layers:
    - type: conv2d
      params: { in_channels: 3, out_channels: 64, kernel_size: 3, padding: 1 }
    - type: batchnorm
      params: { num_features: 64 }
    # ...
  head:
    type: linear
    activation: softmax
    output_neurons: num_classes
training:
  optimizer: AdamW
  lr: 0.001
  loss: CrossEntropyLoss
  batch_size: 16
  epochs: 100
augmentation:
  - RandomHorizontalFlip
  - ToTensor
  - Normalize
```

---

## 6. Data Definitions

### 6.1 Model Definition Schema

```typescript
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

### 6.2 CNN v16 Definition (Full)

See: `src/data/models/cnn_v16.json`

---

## 7. Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial load | < 3s | Lighthouse |
| 3D FPS | ≥ 30 | Chrome DevTools |
| Extension click → panel | < 500ms | User perception |
| Code injection | < 300ms | Console timing |
| Export | < 2s | Console timing |
| Memory usage | < 200MB | Chrome Task Manager |

### Optimization Strategies

| Strategy | Implementation |
|----------|---------------|
| Lazy load 3D assets | React.lazy + Suspense |
| Instance reuse | Shared geometries and materials |
| LOD (Level of Detail) | Simpler geometry when zoomed out |
| Debounce code generation | 100ms debounce on state changes |
| Memoize expensive computations | useMemo for code generation |

---

## 8. Testing Strategy

### 8.1 Unit Tests (Vitest)

| Component | Test |
|-----------|------|
| codeGenerator | Generates correct code for each extension combination |
| notebookBuilder | Produces valid .ipynb JSON |
| yamlExporter | Produces valid YAML |
| Model loader | Loads and validates model definitions |

### 8.2 Component Tests (React Testing Library)

| Component | Test |
|-----------|------|
| ExtensionPanel | Renders options; Apply button works |
| InfoPanel | Updates when extensions change |
| NotebookWindow | Opens/collapses; shows correct code |
| ModelMenu | Lists models; selects correctly |

### 8.3 E2E Tests (Playwright)

| Scenario | Test |
|----------|------|
| Full flow | Select model → configure all → export → notebook is valid |
| Change flow | Change optimizer → code updates → export reflects change |
| Develop mode | Open → freeze layer → export shows frozen layer |

---

## 9. Deployment

### 9.1 Development

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 9.2 Production Build

```bash
npm run build
# Output: frontend/dist/
```

### 9.3 Deployment Options

| Option | Command | Notes |
|--------|---------|-------|
| Vercel | `vercel deploy` | Free tier; automatic HTTPS |
| Netlify | `netlify deploy` | Free tier; form handling |
| GitHub Pages | `npm run build; gh-pages -d dist` | Free; static only |
| Docker | `docker build -t neuroscope .` | Self-hosted |

### 9.4 Docker (Static Site)

```dockerfile
FROM nginx:alpine
COPY frontend/dist /usr/share/nginx/html
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

---

## 10. Development Guidelines

### 10.1 Code Style

- **TypeScript:** Strict mode enabled
- **Components:** Functional components with hooks
- **State:** Zustand for global; useState for local
- **Styling:** Tailwind CSS; no inline styles
- **3D:** React Three Fiber; declarative, not imperative

### 10.2 Git Workflow

```
main
  └── develop
       ├── feature/workspace
       ├── feature/core-engine
       ├── feature/extensions
       ├── feature/notebook
       ├── feature/info-panel
       └── feature/export
```

### 10.3 PR Requirements

- [ ] TypeScript compiles without errors
- [ ] All tests pass
- [ ] Component story (if applicable)
- [ ] Screenshot/recording of visual changes
- [ ] No console errors

---

*Document prepared for DigiNeurons Software Track.*
*For questions, contact: hazemelerefy@gmail.com*
