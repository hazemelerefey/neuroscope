# NeuroScope — Frontend Development Guide

**Stack:** React 18 + TypeScript + Three.js (React Three Fiber) + Zustand + Tailwind CSS (via index.css)
**Last updated:** June 30, 2026 (matches actual implementation)

---

## File Structure

```
frontend/src/
├── types.ts                    # All TypeScript type definitions
├── store.ts                    # Zustand global store (model catalog, extensions, actions)
├── App.tsx                     # Root layout: header, workspace, overlays
├── index.css                   # All styles (CSS variables + component classes)
└── components/
    ├── Canvas3D.tsx            # 3D viewport (R3F): core engine, extensions, cables
    ├── ModelSelector.tsx       # Right-panel model tree picker
    ├── ExtensionConfig.tsx     # Right-panel extension option selector
    ├── NotebookWindow.tsx      # Top-right code viewer overlay
    ├── DevelopMode.tsx         # Bottom-right layer inspector overlay
    └── InfoPanel.tsx           # Bottom bar model summary
```

---

## 1. Component Architecture

```
App
├── header (toolbar: Develop / Notebook / Reset)
└── workspace (flex row)
    ├── canvas-area
    │   └── CanvasErrorBoundary
    │       └── Canvas3D (R3F <Canvas>)
    │           ├── EmptyState (Html overlay, + button)
    │           ├── CoreEngine (rotating box)
    │           ├── ExtensionBlock × 7 (orbiting octahedra)
    │           └── Cable × 7 (dashed lines)
    ├── panel-area (right sidebar, 340px)
    │   ├── ModelSelector (when rightPanelTab === 'model')
    │   └── ExtensionConfig (when rightPanelTab === 'extension')
    ├── develop-panel (absolute overlay, bottom-right)
    │   └── DevelopMode
    ├── notebook-window (absolute overlay, top-right)
    │   └── NotebookWindow
    └── info-panel (absolute, bottom bar)
        └── InfoPanel
```

**Panel switching logic in App.tsx:**
```tsx
{rightPanelTab === 'model' ? (
  <ModelSelector />
) : selectedExtensionKind ? (
  <ExtensionConfig kind={selectedExtensionKind} onClose={handleExtensionClose} />
) : (
  <ModelSelector />
)}
```

Overlays (DevelopMode, NotebookWindow, InfoPanel) are conditionally rendered based on store state.

---

## 2. Components

### 2.1 Canvas3D

**File:** `src/components/Canvas3D.tsx`

**Purpose:** The main 3D viewport. Shows an empty state with a "+" button, or the selected model's core engine block surrounded by orbiting extension octahedra connected by cables.

**Sub-components:**

#### EmptyState
- Rendered via `<Html center>` when no model is selected
- Circular dashed-border "+" button (80×80px, indigo tones)
- Click calls `useStore.getState().setRightPanelTab('model')` to open the model selector
- Hover: solid border + scale(1.05)

#### CoreEngine
- **Props:** `{ model: SelectedModel }`
- Metallic box whose size scales with model complexity: `baseScale = 0.5 + complexity * 0.15`
- Three nested meshes: solid box (opacity 0.85), wireframe overlay, inner emissive glow
- Color per family: CNN=indigo, YOLO=amber, ResNet=green, Transformer=purple, GAN=pink, Autoencoder=cyan
- Label via `<Html>` showing version name, size name, and param count
- **Animation:** Continuous Y-axis rotation (`delta * 0.2`)

#### ExtensionBlock
- **Props:** `{ extension: Extension, index: number, total: number }`
- Octahedron geometry (radius 0.25 unconfigured, 0.35 configured)
- Orbits the origin at radius 3, with slow drift (`time * 0.1`) and Y-axis bob
- Click calls `selectExtension(extension.kind)` to open config panel
- Shows icon + label above, "✓ configured" badge when option selected
- Emissive intensity: 0 (default), 0.2 (configured), 0.5 (selected)

#### Cable
- **Props:** `{ index: number, total: number, color: string }`
- `<Line>` from origin to orbit position (dashed, opacity 0.3, lineWidth 1)
- Static snapshot (not dynamically animated to track moving extensions)

**Canvas config:**
```tsx
<Canvas gl={{ antialias: true }} dpr={[1, 2]}>
  <PerspectiveCamera makeDefault position={[0, 4, 10]} />
  <OrbitControls enableDamping dampingFactor={0.05} />
  {/* ambient + directional + 2 colored point lights */}
  <gridHelper args={[30, 30, '#1e293b', '#0f172a']} />
</Canvas>
```

---

### 2.2 ModelSelector

**File:** `src/components/ModelSelector.tsx`

**Purpose:** Right-panel tree picker for choosing a model family → version → size.

**State:**
- `expandedFamily: string | null` — which family accordion is open
- `expandedVersion: string | null` — which version accordion is open

**Rendering:** Three-level expandable tree:
1. **Family** — icon + name button (e.g. `🔲 CNN`)
2. **Version** — indented sub-button (e.g. `Basic CNN`)
3. **Sizes** — card buttons showing name, param count, description, and a 5-dot complexity indicator

**Selection:** Clicking a size calls:
```tsx
selectModel({ family, version, size })
```

The currently selected size gets a purple border + check icon.

---

### 2.3 ExtensionConfig

**File:** `src/components/ExtensionConfig.tsx`

**Purpose:** Right-panel form for picking an option within an extension (optimizer, loss function, etc.).

**Props:** `{ kind: ExtensionKind, onClose: () => void }`

**Layout:**
- Header with icon + label + close button
- List of option buttons (name + description)
- Selected option expands to show three detail sections:
  - 💡 **When to use** — plain-English guidance
  - ⚡ **Consequences** — trade-offs
  - 📝 **Code** — Python snippet in a `<pre><code>` block

**Behavior:** Clicking an option calls `updateExtensionOption(kind, optionId)` which updates the store and opens the notebook.

---

### 2.4 NotebookWindow

**File:** `src/components/NotebookWindow.tsx`

**Purpose:** Top-right overlay showing generated notebook/config code.

**State:**
- `activeFormat: 'ipynb' | 'yaml'` — tab toggle
- `copied: boolean` — copy feedback
- `content: string` — generated output

**Behavior:**
- Content regenerates via `useEffect` whenever model, extensions, or format change
- **Copy** button uses `navigator.clipboard.writeText`
- **Download** creates a Blob → object URL → programmatic `<a>` click
- Format tabs switch between `.ipynb` (JSON notebook) and `.yaml` (config)

**Rendering:** Fixed at `position: absolute; top: 0; right: 340px; width: 480px; max-height: 55%`.

---

### 2.5 DevelopMode

**File:** `src/components/DevelopMode.tsx`

**Purpose:** Bottom-right overlay showing a layer-by-layer inspector for the selected model.

**State:**
- `expandedLayer: string | null` — which layer's details are visible
- `addAfterId: string | null` — which layer's "add after" menu is open

**Layer list:** Each layer shows:
- Expand chevron → input/output shapes, param count, frozen/trainable status
- Type badge (e.g. `CONV2D`) + name + param count
- Action buttons: ❄️ freeze toggle, ➕ add after, 🗑️ remove (if `removable`)

**Add layer menu:** Offers `ADDABLE_LAYER_TYPES = ['Conv2d', 'Linear', 'BatchNorm2d', 'ReLU', 'GELU', 'Dropout', 'MaxPool2d']`

**Layers are auto-generated** by `selectModel` in the store based on model complexity (see §3).

---

### 2.6 InfoPanel

**File:** `src/components/InfoPanel.tsx`

**Purpose:** Bottom bar showing model summary and configured extension count.

**Layout:**
- Toggle bar: "ℹ️ Model Info" with collapse chevron
- Expanded content (horizontal flex):
  - Model name + icon + description
  - Stats row: Family, Parameters, Complexity (5 dots), Extensions (configured/total)
  - Configured extensions list (icon + label + selected option name)

**Rendering:** `position: absolute; bottom: 0; left: 0; right: 340px`.

---

## 3. State Management (Zustand)

**File:** `src/store.ts`

### 3.1 State Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `modelCatalog` | `ModelFamily[]` | 6 families (CNN, YOLO, ResNet, Transformer, GAN, Autoencoder) | Read-only model catalog |
| `selectedModel` | `SelectedModel \| null` | `null` | Currently selected model |
| `extensions` | `Extension[]` | 7 default extensions | All extension configs with options |
| `selectedExtensionKind` | `ExtensionKind \| null` | `null` | Which extension panel is open |
| `notebookOpen` | `boolean` | `false` | Notebook overlay visibility |
| `developMode` | `boolean` | `false` | Layer inspector visibility |
| `infoPanelCollapsed` | `boolean` | `false` | Info panel collapse state |
| `rightPanelTab` | `'model' \| 'extension'` | `'model'` | Which right panel to show |
| `layers` | `LayerInfo[]` | `[]` | Generated layers for develop mode |

### 3.2 Actions

| Action | Signature | Effect |
|---|---|---|
| `selectModel` | `(model: SelectedModel) => void` | Sets model, generates layers from complexity, opens notebook, resets panel to 'model' |
| `clearModel` | `() => void` | Resets everything: model, layers, extensions, UI state |
| `selectExtension` | `(kind: ExtensionKind) => void` | Sets `selectedExtensionKind`, switches panel to 'extension' |
| `updateExtensionOption` | `(kind, optionId) => void` | Updates extension's `selectedOptionId`, opens notebook |
| `toggleNotebook` | `() => void` | Toggles `notebookOpen` |
| `toggleDevelopMode` | `() => void` | Toggles `developMode` |
| `toggleInfoPanel` | `() => void` | Toggles `infoPanelCollapsed` |
| `setRightPanelTab` | `(tab) => void` | Sets `rightPanelTab` |
| `toggleLayerFrozen` | `(layerId) => void` | Flips layer's `frozen` boolean |
| `removeLayer` | `(layerId) => void` | Removes layer from `layers` array |
| `addLayer` | `(afterId, layerType) => void` | Inserts new layer after specified ID |
| `exportNotebook` | `(format: ExportFormat) => string` | Generates `.ipynb` JSON or `.yaml` config string |
| `reset` | `() => void` | Full state reset to defaults |

### 3.3 Layer Generation (in `selectModel`)

Layers are generated based on `model.size.complexity` (1–5):
- For each block `0..complexity`: Conv2d → BatchNorm2d → ReLU → MaxPool2d (except last block)
- Final: Flatten → Linear (output 10 classes)
- Channel count scales: `64 * (block + 1)`
- First Conv2d is non-removable; all others are removable

### 3.4 Model Catalog

Six families, each with versions and sizes:

| Family | Icon | Versions | Sizes |
|---|---|---|---|
| CNN | 🔲 | Basic CNN | Nano (~100K) → X-Large (~50M) |
| YOLO | 👁️ | YOLOv5, YOLOv8 | Nano (~1.9M/3.2M) → X-Large (~87M/68M) |
| ResNet | 🔗 | ResNet | ResNet-18 (~11M) → ResNet-152 (~60M) |
| Transformer | 🤖 | ViT | ViT-S/16 (~22M) → ViT-L/16 (~307M) |
| GAN | 🎨 | DCGAN | Small (~3M) → Large (~50M) |
| Autoencoder | 🔄 | VAE | Small (~1M) → Large (~20M) |

Each `ModelSize` has a `complexity` rating (1–5) that drives 3D block size and layer count.

### 3.5 Default Extensions

| Kind | Icon | Color | Options |
|---|---|---|---|
| `optimizer` | ⚡ | `#f59e0b` | Adam, SGD + Momentum, AdamW |
| `activation` | 📈 | `#8b5cf6` | ReLU, GELU, SiLU/Swish, Leaky ReLU |
| `loss` | 🎯 | `#ef4444` | Cross Entropy, MSE, BCE With Logits, Focal Loss |
| `lr_scheduler` | 📉 | `#06b6d4` | Cosine Annealing, Step LR, Reduce On Plateau |
| `batch_size` | 📦 | `#10b981` | 16, 32, 64, 128 |
| `epochs` | 🔁 | `#f97316` | 10, 50, 100, 300 |
| `augmentation` | 🔀 | `#ec4899` | None, Basic, Advanced (AutoAugment) |

Each option includes: `id`, `name`, `description`, `whenToUse`, `consequences`, `code` (Python snippet).

Extensions are positioned at evenly spaced angles (0°, 51°, 102°, 153°, 204°, 255°, 306°) at distance 3.

---

## 4. Types

**File:** `src/types.ts`

### Model Types

```typescript
type ModelFamilyId = 'cnn' | 'yolo' | 'resnet' | 'transformer' | 'gan' | 'autoencoder'

interface ModelFamily {
  id: ModelFamilyId
  name: string
  icon: string
  description: string
  versions: ModelVersion[]
}

interface ModelVersion {
  id: string        // e.g. "yolov5"
  name: string      // e.g. "YOLOv5"
  sizes: ModelSize[]
}

type ModelSizeId = 'nano' | 'small' | 'medium' | 'large' | 'xlarge'

interface ModelSize {
  id: ModelSizeId
  name: string
  params: string         // e.g. "~3.2M"
  description: string
  complexity: 1 | 2 | 3 | 4 | 5  // drives 3D block size + layer count
}

interface SelectedModel {
  family: ModelFamily
  version: ModelVersion
  size: ModelSize
}
```

### Extension Types

```typescript
type ExtensionKind =
  | 'optimizer' | 'activation' | 'loss' | 'lr_scheduler'
  | 'batch_size' | 'epochs' | 'augmentation'

interface ExtensionOption {
  id: string
  name: string
  description: string
  whenToUse: string
  consequences: string
  code: string           // Python code snippet
}

interface Extension {
  kind: ExtensionKind
  label: string
  icon: string
  options: ExtensionOption[]
  selectedOptionId: string | null
  position: { angle: number; distance: number }
  color: string          // hex color for cable + block
}
```

### Layer Types (Develop Mode)

```typescript
interface LayerInfo {
  id: string
  name: string
  type: string           // "Conv2d", "BatchNorm2d", "ReLU", etc.
  params: number
  frozen: boolean
  removable: boolean
  inputShape: string     // e.g. "[B, 64, H, W]"
  outputShape: string
}
```

### Other Types

```typescript
type ExportFormat = 'ipynb' | 'yaml'

interface WorkspaceState {
  selectedModel: SelectedModel | null
  extensions: Extension[]
  notebookOpen: boolean
  developMode: boolean
  infoPanelCollapsed: boolean
  rightPanelTab: 'model' | 'extension'
  selectedExtensionKind: ExtensionKind | null
}
```

Legacy types (`LayerNode`, `Edge`, `GraphData`) are retained for backward compatibility but unused by the current frontend.

---

## 5. 3D Rendering Details

### Empty State
- `<Html center>` overlay with a dashed-circle "+" button
- Indigo color scheme (`rgba(99,102,241,...)`)
- Click triggers `setRightPanelTab('model')` to show the model selector

### Core Engine Block
- `boxGeometry` scaled by `0.5 + complexity * 0.15` (range: 0.65 → 1.25)
- Three-layer rendering: solid material (opacity 0.85, metalness 0.6) → wireframe overlay → inner emissive glow
- Color mapped from `family.id` to a hex color
- Continuous Y rotation at `0.2 rad/s`
- HTML label above showing version name + size + params

### Extension Octahedra
- `octahedronGeometry` — radius 0.25 (unconfigured) or 0.35 (configured)
- Orbit at radius 3 with slow angular drift (`time * 0.1`) and Y-axis sine bob
- Color from `extension.color`
- Emissive intensity: 0 → 0.2 → 0.5 based on state
- Click handler opens extension config panel

### Cables
- `<Line>` (drei) from origin to orbit position
- Dashed pattern (dashSize 0.1, gapSize 0.1), opacity 0.3
- Static — do not dynamically track moving extensions (computed once via `useMemo`)

### Lighting
```tsx
<ambientLight intensity={0.4} />
<directionalLight position={[10, 10, 5]} intensity={1.2} />
<pointLight position={[-10, -5, -5]} intensity={0.3} color="#8b5cf6" />
<pointLight position={[5, -10, 5]} intensity={0.3} color="#06b6d4" />
```

### Grid
- `gridHelper` 30×30, colors `#1e293b` / `#0f172a`

---

## 6. Styling

**File:** `src/index.css` — all styles are CSS (no Tailwind utility classes in components).

### CSS Variables

```css
--bg-primary: #0f172a        /* Main background */
--bg-secondary: #1e293b      /* Panels, cards */
--bg-card: #1e293b
--bg-hover: #263548          /* Hover state */
--text-primary: #f8fafc
--text-secondary: #94a3b8
--text-muted: #64748b
--accent-blue: #3b82f6
--accent-purple: #8b5cf6
--accent-green: #10b981
--accent-red: #ef4444
--accent-yellow: #f59e0b
--accent-cyan: #06b6d4
--accent-pink: #ec4899
--accent-orange: #f97316
--border: #334155
--border-light: #475569
--radius: 8px / --radius-sm: 4px / --radius-lg: 12px
```

### Layout

- **App shell:** Full viewport, flex column
- **Header:** `padding: 12px 20px`, gradient title text, toolbar buttons on right
- **Workspace:** Flex row, `height: calc(100vh - 58px)`
- **Canvas area:** `flex: 1`
- **Panel area:** Fixed `width: 340px`, right sidebar with `border-left`

### Key Animations

```css
@keyframes slideDown { from { opacity: 0; transform: translateY(-4px); } }
@keyframes slideUp   { from { transform: translateY(20px); opacity: 0; } }
```

### Responsive Breakpoints

| Breakpoint | Changes |
|---|---|
| `≤ 1024px` | Panel width → 280px, notebook/develop/info right offset → 280px |
| `≤ 768px` | Header stacks vertically, workspace becomes column (canvas 50vh, panel 40vh), overlays go full-width |

### Scrollbar

Custom WebKit scrollbar: 6px width, `--border` thumb, transparent track.

---

## 7. Data Flow

### Model Selection
```
User clicks size in ModelSelector
  → selectModel({ family, version, size })
  → store sets selectedModel, generates layers, sets notebookOpen=true, rightPanelTab='model'
  → Canvas3D re-renders: EmptyState → CoreEngine + ExtensionBlocks + Cables
  → InfoPanel appears at bottom
  → NotebookWindow appears at top-right
```

### Extension Configuration
```
User clicks extension octahedron in Canvas3D
  → selectExtension(kind)
  → store sets selectedExtensionKind, rightPanelTab='extension'
  → ModelSelector replaced by ExtensionConfig in panel area
User clicks an option
  → updateExtensionOption(kind, optionId)
  → store updates extension.selectedOptionId, sets notebookOpen=true
  → ExtensionBlock grows (0.25 → 0.35 radius), emissive increases
  → NotebookWindow content regenerates
  → InfoPanel updates configured count
```

### Code Generation
```
exportNotebook('ipynb') iterates all extensions with selectedOptionId
  → builds JSON notebook with markdown + code cells
exportNotebook('yaml') builds flat YAML config
  → called by NotebookWindow useEffect on model/extension/format change
```

### Layer Editing (Develop Mode)
```
User clicks Develop toolbar button
  → toggleDevelopMode()
  → DevelopMode overlay appears with layer list
User toggles freeze / removes / adds layer
  → store updates layers array
  → (layers are local state; no code regeneration yet)
```

### Reset
```
User clicks Reset toolbar button
  → clearModel()
  → resets: selectedModel, layers, extensions (clear selections), all UI flags
  → Canvas3D returns to EmptyState
```

---

## 8. App.tsx Layout

The root component orchestrates everything:

- **Header:** NeuroScope title (gradient) + toolbar buttons (Develop, Notebook, Reset — only shown when model selected)
- **Workspace:** Flex row containing canvas-area + panel-area + overlays
- **CanvasErrorBoundary:** Class component wrapping Canvas3D — catches R3F errors, shows fallback with "Try Again" button
- **Panel area:** Switches between ModelSelector and ExtensionConfig based on `rightPanelTab`
- **Overlays:** DevelopMode (bottom-right), NotebookWindow (top-right), InfoPanel (bottom) — absolutely positioned, conditionally rendered

---

## 9. Export

Two formats via `store.exportNotebook(format)`:

**`.ipynb`** — Valid Jupyter notebook JSON:
- Markdown cell with model name, family, params, description
- Code cell with imports
- Per configured extension: markdown cell (label, description, when-to-use) + code cell (Python snippet)

**`.yaml`** — Flat config:
```yaml
model:
  family: cnn
  version: cnn-basic
  size: medium
  name: "Basic CNN Medium"
  params: "~2M"
extensions:
  optimizer: adam
  loss: cross_entropy
```
