# NeuroScope — Brief Vision

## What is NeuroScope?
A visual tool for building deep learning models **without writing code**. The user configures a model through a 3D interactive UI, and exports a ready-to-run notebook.

**The app does NOT run code or load datasets.** It only generates/displays code.

---

## Core Flow

```
[Empty Workspace + Plus Sign]
        ↓ Click or Drag & Drop
[Select Model: Family → Version → Size]
        ↓
[Core Engine activates + Extensions load]
        ↓
[Click each Extension → Choose option → Apply]
        ↓
[Code injects into Notebook + Info updates]
        ↓
[Export: .ipynb / .yaml / other formats]
        ↓
[User runs on Colab or locally]
```

---

## Key Components

### Workspace
- Empty canvas with `+` button (like n8n)
- Right panel: models list (collapsible, hides after selection)
- Drag & drop OR click to place model

### Core Engine
- 3D block that powers on when model selected
- Click → Options: Add Model (future), Change (future), Custom (Develop Mode)
- Size affects 3D complexity (more layers = bigger geometry)

### Develop Mode
- View all model layers + full code
- Freeze/Unfreeze/Remove/Add layers
- **Head Layer** visible in both Develop Mode AND main UI

### Extensions
- Satellite blocks around Core Engine, connected by cables
- Each model has **its own set** of extensions
- Click → Right panel opens → Choose → Apply → Code injects
- Example: YOLO has NMS, CNN does not

### Info Panel
- Shows model details on load
- Updates when any extension is added
- Head layer info always visible (default head + activation function)

### Notebook Window
- Collapsible, top-right corner
- Auto-opens on model selection and on every change
- Editable code view

---

## Export
- **.ipynb** — Jupyter Notebook (Colab-ready)
- **.yaml** — Model definition
- User adds dataset imports + environment setup after export

---

## Design
- Cyberpunk aesthetic (dark, neon glow)
- Colors: Green (Training), Purple (Data), Yellow (Functional), Blue (Core)
- Cables glow when extension is activated
- Educational info on every option

---

## Scope
- **Now:** CNN only
- **Future:** YOLO, ResNet, EfficientNet, Custom models, Multi-modal, GPU backend

---

*Last updated: June 29, 2026*
