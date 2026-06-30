# NeuroScope — Complete User Experience Document

**Purpose:** Ultra-detailed walkthrough of every screen, interaction, click, animation, and state.  
**For:** Software Team (Shahd, Mohamed Wagdi, Ziad, Yossef Safout)  
**Version:** 1.0 — June 30, 2026

---

## Table of Contents

1. [App Launch & First Load](#1-app-launch--first-load)
2. [Empty Workspace](#2-empty-workspace)
3. [Opening the Model Selector](#3-opening-the-model-selector)
4. [Selecting a Model — The Full Flow](#4-selecting-a-model--the-full-flow)
5. [The 3D Machine Appears](#5-the-3d-machine-appears)
6. [Extension Configuration](#6-extension-configuration)
7. [The Notebook Window](#7-the-notebook-window)
8. [The Info Panel](#8-the-info-panel)
9. [Validation Warnings](#9-validation-warnings)
10. [Develop Mode](#10-develop-mode)
11. [Exporting](#11-exporting)
12. [Changing the Model](#12-changing-the-model)
13. [Responsive Behavior](#13-responsive-behavior)
14. [Animations & Transitions Reference](#14-animations--transitions-reference)
15. [Keyboard Shortcuts](#15-keyboard-shortcuts)
16. [Edge Cases & Error States](#16-edge-cases--error-states)

---

## 1. App Launch & First Load

### What the user sees:

The browser loads `http://localhost:5173`. The screen is **completely dark** (#0a0a0f). A subtle loading animation plays — a thin horizontal line that sweeps left to right across the center of the screen, colored in the primary accent (#6366f1 indigo). This lasts 1-2 seconds maximum.

### What happens in the background:

- React app hydrates
- Zustand store initializes with `selectedModel: null`
- Three.js canvas initializes (but renders nothing yet)
- Model catalog loads from static data in the store (no API call needed for the catalog — it's hardcoded in `store.ts`)

### After load completes:

The loading line fades out. The workspace appears — a dark, empty 3D canvas with a single glowing `+` button in the center.

---

## 2. Empty Workspace

### Layout:

```
┌─────────────────────────────────────────────────────────────┐
│  (no header bar — full viewport)                            │
│                                                             │
│                                                             │
│                     ┌───┐                                   │
│                     │ + │  ← centered, floating             │
│                     └───┘                                   │
│                                                             │
│                                                             │
│                                                             │
│  [Info Panel: "No model selected"]                         │
└─────────────────────────────────────────────────────────────┘
```

### The `+` Button:

- **Position:** Dead center of the viewport
- **Shape:** 80×80px circle
- **Border:** 2px dashed, rgba(99, 102, 241, 0.5) — a soft indigo
- **Background:** Transparent
- **Icon:** A large `+` character, 36px, rgba(99, 102, 241, 0.7)
- **Cursor:** Pointer (hand icon)
- **Hover effect:** Border brightens to full #6366f1, background gets a subtle rgba(99, 102, 241, 0.08) fill, the `+` scales up 1.1x. Transition: 0.2s ease.
- **Click behavior:** Opens the Model Selector in the right panel

### Info Panel (bottom):

- **Position:** Fixed to the bottom of the viewport, full width
- **Height:** 48px
- **Background:** rgba(10, 10, 15, 0.9) with backdrop-blur
- **Border-top:** 1px solid rgba(255, 255, 255, 0.06)
- **Content (centered):** "No model selected" in muted text (#6b7280), 13px
- **Font:** Inter

### Ambient Atmosphere:

- The 3D canvas has a very subtle star field or particle effect in the background (optional — low priority). If not implemented, the background is pure #0a0a0f.
- No sound effects.

---

## 3. Opening the Model Selector

### Trigger:

User clicks the `+` button in the center, OR clicks the right panel tab (if visible).

### What happens:

1. The `+` button **fades out** (opacity 0, 0.2s)
2. A **right panel slides in** from the right edge
   - Width: 320px
   - Background: rgba(15, 15, 25, 0.95) with backdrop-blur
   - Border-left: 1px solid rgba(255, 255, 255, 0.06)
   - Slide-in animation: translateX(100%) → translateX(0), 0.3s ease-out
3. The panel shows the **Model Selector** content

### Model Selector — Panel Layout:

```
┌──────────────────────────────┐
│  ← Close          Models     │  ← header (48px)
├──────────────────────────────┤
│                              │
│  🔲 CNN                      │  ← family card
│  Convolutional Neural...     │
│  ─────────────────────────── │
│  👁️ YOLO                     │  ← family card
│  You Only Look Once...       │
│  ─────────────────────────── │
│  🔗 ResNet                   │
│  Residual Networks...        │
│  ─────────────────────────── │
│  ⚡ EfficientNet             │
│  Efficient scaling...        │
│  ─────────────────────────── │
│  🌲 Decision Tree            │
│  Classical ML...             │
│  ─────────────────────────── │
│  🌲 Random Forest            │
│  Ensemble method...          │
│                              │
└──────────────────────────────┘
```

### Family Card:

- **Height:** ~72px
- **Padding:** 16px
- **Layout:** Icon (left) + Name (bold, 15px) + Description (muted, 12px, 1 line, ellipsis)
- **Background:** Transparent
- **Hover:** Background becomes rgba(255, 255, 255, 0.04), cursor pointer
- **Click:** Expands to show versions

### When user clicks a family (e.g., CNN):

The family card **expands in place** with a smooth height animation (0.2s). Other families stay visible but dimmed (opacity 0.5). The expanded card shows:

```
┌──────────────────────────────┐
│  🔲 CNN                      │
│  Convolutional Neural...     │
│                              │
│  ┌────────────────────────┐  │
│  │  Basic CNN             │  │  ← version card
│  │  Standard CNN          │  │
│  └────────────────────────┘  │
│                              │
└──────────────────────────────┘
```

### When user clicks a version (e.g., Basic CNN):

The version card **expands** to show size options:

```
┌──────────────────────────────┐
│  🔲 CNN                      │
│  Convolutional Neural...     │
│                              │
│  Basic CNN                   │
│                              │
│  ┌────────────────────────┐  │
│  │  🔹 Nano    ~100K     │  │  ← size option
│  │  2 conv layers         │  │
│  ├────────────────────────┤  │
│  │  🔹 Small   ~500K     │  │
│  │  4 conv layers         │  │
│  ├────────────────────────┤  │
│  │  🔹 Medium  ~2M       │  │
│  │  6 conv layers + pool  │  │
│  ├────────────────────────┤  │
│  │  🔹 Large   ~10M      │  │
│  │  8+ conv layers        │  │
│  ├────────────────────────┤  │
│  │  🔹 X-Large ~50M      │  │
│  │  Deep CNN + skip       │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

### Size Option:

- **Height:** ~56px
- **Layout:** Dot indicator (left) + Name (bold) + Param count (right, muted) + Description (below, muted, 12px)
- **Hover:** Background rgba(99, 102, 241, 0.08), dot brightens
- **Click:** **This is the moment the model is selected.** See next section.

---

## 4. Selecting a Model — The Full Flow

### When user clicks a size (e.g., "Medium"):

This triggers a **sequence of events** that takes about 1.5 seconds total:

### Step 1: Panel closes (0.3s)

- The right panel slides back out (translateX(0) → translateX(100%))
- The `+` button does NOT reappear (model is now selected)

### Step 2: 3D machine builds (1.0s)

- The core engine block **fades in** at the center of the canvas (opacity 0 → 1, scale 0.8 → 1.0)
- The block pulses once with a soft glow effect (box shadow expands then contracts)
- Extensions **orbit in** one by one from outside the viewport:
  - Each extension starts at a random position outside the canvas
  - It travels along a curved path to its final orbiting position
  - Stagger: 100ms between each extension arriving
  - Duration: 0.5s per extension
- Cables **draw in** between the core engine and each extension:
  - The cable starts as a 0-length line at the core engine
  - It extends outward to reach the extension (0.3s, ease-out)
  - Once connected, the cable pulses with a subtle light traveling along it

### Step 3: Notebook window auto-opens (0.5s delay)

- After the machine is built, the notebook window slides in from the top-right
- See [Section 7: Notebook Window](#7-the-notebook-window) for details

### Step 4: Info panel updates (immediate)

- The bottom info panel updates to show the model name and basic stats
- See [Section 8: Info Panel](#8-the-info-panel) for details

---

## 5. The 3D Machine Appears

### The Core Engine Block:

- **Shape:** Rounded box (RoundedBox geometry in Three.js)
- **Size:** Varies by model complexity:
  - Nano: 1.0 × 0.6 × 1.0
  - Small: 1.2 × 0.7 × 1.2
  - Medium: 1.4 × 0.8 × 1.4
  - Large: 1.6 × 0.9 × 1.6
  - X-Large: 1.8 × 1.0 × 1.8
- **Color:** Dark indigo (#1e1b4b) with a subtle gradient to lighter indigo on top
- **Material:** MeshStandardMaterial with metalness: 0.3, roughness: 0.7
- **Edges:** Soft white edge glow (bloom effect, low intensity)
- **Text on block:** Model name (e.g., "CNN v16") rendered as a text sprite above the block
- **Rotation:** Slow continuous rotation (0.001 rad/frame around Y axis) — can be paused by clicking the block
- **Hover:** Block brightens slightly, tooltip appears showing model name + description

### The Extensions:

Each extension is a **smaller 3D shape** that orbits the core engine at a fixed distance and height.

- **Shape:** Octahedron (8-faced geometric shape)
- **Size:** 0.25 radius
- **Color:** Each extension has its own color:
  - ⚡ Optimizer: Amber (#f59e0b)
  - 🔥 Activation: Orange (#f97316)
  - 💚 Loss: Green (#22c55e)
  - 📈 Learning Rate: Blue (#3b82f6)
  - 📦 Batch Size: Purple (#8b5cf6)
  - 🔄 Epochs: Cyan (#06b6d4)
  - 🟣 Augmentation: Pink (#ec4899)
- **Orbit radius:** 2.5 units from center
- **Orbit speed:** Very slow (0.0005 rad/frame)
- **Orbit height:** Each extension is at a slightly different Y position (staggered by 0.3 units) to avoid overlap
- **Hover:** Extension brightens, tooltip shows name + current selection (e.g., "Optimizer: AdamW")
- **Click:** Opens the configuration panel for that extension (see Section 6)

### The Cables:

- **Shape:** Tube geometry connecting core engine to each extension
- **Color:** Same as the extension it connects to, but at 50% opacity
- **Width:** 0.02 radius
- **Behavior:** The cable follows the extension as it orbits (dynamic geometry update each frame)
- **Pulse effect:** A small light particle travels along the cable from core to extension every 3 seconds

### Camera:

- **Position:** Slightly elevated, looking down at the machine from a ~30° angle
- **Default position:** (0, 2, 5)
- **Controls:** OrbitControls enabled — user can rotate, zoom, pan
  - Left click + drag: Rotate around the machine
  - Scroll: Zoom in/out
  - Right click + drag: Pan
- **Reset:** Double-click anywhere to reset camera to default position

### Lighting:

- **Ambient light:** Low intensity (0.3) — keeps the scene from being too dark
- **Point light 1:** Positioned above and to the left (#6366f1, intensity 0.8) — indigo tint
- **Point light 2:** Positioned below and to the right (#8b5cf6, intensity 0.4) — purple fill
- **Spot light:** Directly above, pointing down at the core engine (intensity 0.5) — highlights the main block

---

## 6. Extension Configuration

### Trigger:

User clicks an extension octahedron in the 3D scene, OR clicks an extension in the Info Panel.

### What happens:

1. The 3D scene **dims slightly** (background opacity drops 20%)
2. A **configuration panel slides in** from the right (same position as the model selector)
3. The clicked extension **glows brighter** in the 3D scene (to indicate it's being configured)

### Configuration Panel Layout:

```
┌──────────────────────────────┐
│  ← Back        Optimizer ⚡  │  ← header (48px) with extension icon
├──────────────────────────────┤
│                              │
│  Current: AdamW              │  ← current selection badge
│                              │
│  ┌────────────────────────┐  │
│  │  SGD                   │  │  ← option card
│  │  Classic optimizer     │  │
│  │  Slow but generalizes  │  │
│  │  well...               │  │
│  │                        │  │
│  │  When to use:          │  │
│  │  Use when you want...  │  │
│  │                        │  │
│  │  Consequences:         │  │
│  │  Requires careful LR   │  │
│  │  tuning...             │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │  Adam ✓                │  │  ← selected option (highlighted border)
│  │  Adaptive learning...  │  │
│  │  ...                   │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │  AdamW                 │  │  ← default option
│  │  Adam with proper...   │  │
│  │  ...                   │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │  RMSprop               │  │
│  │  Adaptive method...    │  │
│  │  ...                   │  │
│  └────────────────────────┘  │
│                              │
└──────────────────────────────┘
```

### Option Card:

- **Height:** Auto (depends on content, typically 120-160px)
- **Padding:** 16px
- **Border:** 1px solid rgba(255, 255, 255, 0.06)
- **Border-radius:** 8px
- **Background:** Transparent
- **Hover:** Background rgba(255, 255, 255, 0.03), border brightens
- **Selected state:** Border becomes the extension's color (e.g., amber for optimizer), background gets a subtle tint of that color (rgba(245, 158, 11, 0.05)), a small checkmark (✓) appears next to the name
- **Click:** Selects this option → triggers code injection into notebook

### Content of each option card:

1. **Name** (bold, 15px) — e.g., "AdamW"
2. **One-line description** (muted, 13px) — e.g., "Adam with proper weight decay"
3. **"When to use"** section (12px, slightly dimmer) — 1-2 sentences
4. **"Consequences"** section (12px, slightly dimmer) — 1-2 sentences
5. **Code preview** (monospace, 11px, in a dark code block) — the actual PyTorch line

### What happens when user selects an option:

1. The option card animates to "selected" state (border color change, 0.2s)
2. The previous selection animates back to "unselected" state
3. The 3D extension octahedron **flashes** its color briefly (opacity pulse)
4. The cable between core engine and this extension **pulses** with a bright light
5. The notebook window updates (if open) — the relevant code line changes
6. The info panel updates the extension summary
7. A **subtle toast notification** appears at the bottom: "Optimizer set to AdamW" (auto-dismiss after 2s)

### Back button:

Clicking "← Back" in the header slides the panel out and returns to the model selector (if no model is selected) or closes the panel entirely (if a model is already selected).

---

## 7. The Notebook Window

### Position:

- **Top-right corner** of the viewport
- **Default state:** Collapsed (just a tab visible)
- **Size when expanded:** 420px wide × 80% of viewport height

### Collapsed State:

```
┌─────────┐
│  📓 Code │  ← tab button, always visible
└─────────┘
```

- **Tab size:** 100px × 36px
- **Background:** rgba(15, 15, 25, 0.9)
- **Border:** 1px solid rgba(255, 255, 255, 0.06)
- **Border-radius:** 8px (bottom-left, bottom-right)
- **Icon:** Notebook emoji (📓) + "Code" text
- **Hover:** Background brightens slightly
- **Click:** Expands the notebook window

### Expanded State:

```
┌──────────────────────────────┐
│  📓 Code        [ipynb][yaml]│  ← header with format tabs
├──────────────────────────────┤
│  # MyCNN                     │
│  # Generated by NeuroScope   │
│  # Architecture: CNN v16     │
│  # Layers: 16                │
│  # Classes: 10               │
│  │                           │
│  import torch                │
│  import torch.nn as nn       │
│  import torch.optim as optim │
│  │                           │
│  class CustomModel(nn.Module)│
│      def __init__(self, ...): │
│          super().__init__()  │
│          self.conv1 = nn...  │
│          self.bn1 = nn...    │
│          self.act1 = nn...   │
│          ...                 │
│      def forward(self, x):   │
│          x = self.conv1(x)   │
│          ...                 │
│  │                           │
│  # Training Configuration    │
│  optimizer = optim.AdamW(...) │
│  criterion = nn.CrossEntropy │
│  │                           │
│  # Training Loop             │
│  for epoch in range(...):    │
│      ...                     │
│                              │
├──────────────────────────────┤
│  [↓ Download]    [× Close]   │  ← footer
└──────────────────────────────┘
```

### Format Tabs:

- **ipynb tab:** Shows the Jupyter notebook format (cells with markdown + code)
- **yaml tab:** Shows the YAML configuration format
- **Active tab:** Underline in accent color (#6366f1)
- **Click:** Switches the displayed code format

### Code Display:

- **Font:** JetBrains Mono or Fira Code (monospace)
- **Font size:** 12px
- **Line height:** 1.6
- **Colors:** Dark theme syntax highlighting (VS Code Dark+ inspired)
  - Keywords: #c586c0 (purple)
  - Strings: #ce9178 (orange)
  - Functions: #dcdcaa (yellow)
  - Comments: #6a9955 (green)
  - Numbers: #b5cea8 (light green)
  - Types: #4ec9b0 (teal)
- **Line numbers:** Visible, muted gray (#6b7280), 11px
- **Scrollable:** Vertical scroll with custom scrollbar (thin, dark)

### Live Updates:

When the user changes any extension configuration:
1. The affected code line **highlights briefly** (background flashes to rgba(99, 102, 241, 0.15) for 0.5s)
2. The code content updates in place (no full re-render)
3. If the notebook is collapsed, the tab **pulses** briefly to indicate a change

### Footer:

- **Download button:** Icon (↓) + "Download" text. Click downloads the file as `.ipynb` or `.yaml`
- **Close button:** × icon. Click collapses the notebook back to the tab

### Auto-open behavior:

- When a model is first selected, the notebook **auto-expands** after 0.5s delay
- After the first auto-open, it stays at whatever state the user left it in
- If the user closes it, it stays closed until they click the tab again

---

## 8. The Info Panel

### Position:

- **Bottom of the viewport**, full width
- **Height:** 48px (expandable to 120px on click)
- **Background:** rgba(10, 10, 15, 0.9) with backdrop-blur
- **Border-top:** 1px solid rgba(255, 255, 255, 0.06)

### Collapsed State (default):

```
┌─────────────────────────────────────────────────────────────────────┐
│  CNN v16 · 16 layers · Head: Softmax · ⚡ AdamW · 💚 CrossEntropy  │
└─────────────────────────────────────────────────────────────────────┘
```

- **Font:** Inter, 13px
- **Layout:** Horizontal list of key-value pairs separated by `·` dots
- **Content:**
  - Model name (bold)
  - Layer count
  - Head activation
  - Each extension shows its icon + current selection (truncated if too long)
- **Click:** Expands to show full details

### Expanded State:

```
┌─────────────────────────────────────────────────────────────────────┐
│  CNN v16 · 16 layers · Head: Softmax                    ▲ Collapse │
├─────────────────────────────────────────────────────────────────────┤
│  ⚡ Optimizer: AdamW     🔥 Activation: ReLU     💚 Loss: CE       │
│  📈 LR: 0.001           📦 Batch: 32            🔄 Epochs: 100     │
│  🟣 Augmentation: Basic                                              │
│                                                                     │
│  Total Parameters: ~2.5M    Estimated FLOPs: ~1.2G                  │
└─────────────────────────────────────────────────────────────────────┘
```

- **Grid layout:** 3 columns for extensions, each showing icon + name + selection
- **Stats row:** Total parameters and estimated FLOPs (calculated from model definition)
- **Click on any extension:** Opens that extension's configuration panel

---

## 9. Validation Warnings

### When they appear:

The builder rules engine checks the current model configuration against `builder_rules.yaml` rules. Warnings appear when the user:
- Selects a model
- Changes an extension configuration
- Enters develop mode and modifies layers

### Warning Display:

Warnings appear in **two places**:

#### 1. Inline in the 3D scene:

A small **warning icon** (⚠️) appears next to the relevant extension octahedron. Hovering the icon shows a tooltip with the warning message.

#### 2. Toast notification:

```
┌─────────────────────────────────────────────────┐
│  ⚠️  Consider ReLU instead of Sigmoid —         │
│     sigmoid can cause vanishing gradients in    │
│     deep networks.                              │
│                                        [Dismiss] │
└─────────────────────────────────────────────────┘
```

- **Position:** Bottom-right, above the info panel
- **Duration:** 5 seconds (auto-dismiss) or until user clicks Dismiss
- **Animation:** Slides in from the right (0.3s), slides out on dismiss (0.2s)
- **Color:** Warning border (amber for WARNING, red for ERROR, blue for INFO)

### Warning Severity:

| Severity | Border Color | Icon | Behavior |
|----------|-------------|------|----------|
| ERROR | Red (#ef4444) | ❌ | Blocks export until fixed |
| WARNING | Amber (#f59e0b) | ⚠️ | Shows warning, allows export |
| INFO | Blue (#3b82f6) | ℹ️ | Informational, auto-dismiss |

---

## 10. Develop Mode

### Trigger:

User clicks the "Develop" toggle button in the top-left corner of the viewport.

### Toggle Button:

- **Position:** Top-left, 16px from edges
- **Size:** 36px × 36px
- **Icon:** Code brackets (</>)
- **Background:** rgba(15, 15, 25, 0.8)
- **Border:** 1px solid rgba(255, 255, 255, 0.1)
- **Border-radius:** 8px
- **Hover:** Background brightens
- **Active state:** Background becomes accent color (#6366f1), icon turns white

### What happens when Develop Mode activates:

1. The 3D scene **transitions** to a flat layer list view (0.5s animation)
   - The 3D machine blocks flatten into horizontal bars
   - Extensions move to a sidebar
   - The camera transitions to a top-down orthographic view
2. A **layer panel** appears on the left side

### Layer Panel Layout:

```
┌──────────────────────────────────────┐
│  Develop Mode              [× Close] │
├──────────────────────────────────────┤
│                                      │
│  1. Conv2d_1          [❄️] [×]      │
│     nn.Conv2d(3, 64, kernel=3)      │
│                                      │
│  2. BatchNorm_1       [❄️] [×]      │
│     nn.BatchNorm2d(64)              │
│                                      │
│  3. Activation_1      [ ] [×]      │
│     nn.ReLU(inplace=True)           │
│                                      │
│  4. Conv2d_2          [❄️] [×]      │
│     nn.Conv2d(64, 64, kernel=3)     │
│                                      │
│  5. BatchNorm_2       [❄️] [×]      │
│     nn.BatchNorm2d(64)              │
│                                      │
│  ...                                 │
│                                      │
│  16. Flatten          [ ] [×]       │
│                                      │
│  ─────────────────────────────────── │
│  Head: nn.LazyLinear(10)            │
│  Activation: Softmax                 │
│                                      │
│  [+ Add Layer]                       │
│                                      │
└──────────────────────────────────────┘
```

### Layer Row:

- **Number:** Layer order (1-16)
- **Name:** Layer type + number (e.g., "Conv2d_1")
- **Code:** Monospace, muted, the PyTorch code line
- **Freeze button (❄️):** Toggle. When frozen:
  - The ❄️ icon turns blue
  - The row gets a subtle blue tint
  - In the exported notebook, this layer gets `param.requires_grad = False`
- **Remove button (×):** Removes the layer from the architecture
  - Confirmation dialog: "Remove Conv2d_1? This will also remove connected BatchNorm_1."
  - The layer row animates out (height → 0, opacity → 0, 0.2s)
  - Connected layers (e.g., Conv → BN → Act) are suggested for removal together
- **Add Layer button:** Opens a dropdown to add a new layer at the end:
  - Conv2d, BatchNorm, Activation, Pooling, Dropout, Linear
  - Clicking adds a new layer with default parameters

### What happens when Develop Mode deactivates:

1. The layer panel slides out (0.3s)
2. The flat layer bars **lift back into 3D** (reverse of the activation animation)
3. The camera transitions back to the 3D perspective view
4. The 3D machine reflects any changes made (removed layers are gone, frozen layers have a frost effect)

---

## 11. Exporting

### Trigger:

User clicks the "Download" button in the notebook window footer, OR clicks an export button in the top toolbar.

### Export Flow:

1. User clicks "Download"
2. A **format selection dropdown** appears (if not already in the notebook window):
   - "Jupyter Notebook (.ipynb)"
   - "YAML Configuration (.yaml)"
3. User selects a format
4. A **loading indicator** appears (spinning circle, 0.5-1s)
5. The file **downloads** to the user's default download folder
6. A **success toast** appears: "MyCNN.ipynb downloaded successfully" (green border, auto-dismiss 3s)

### Export Button (Top Toolbar):

- **Position:** Top-right, next to the notebook tab
- **Icon:** Download arrow (↓)
- **Size:** 36px × 36px
- **Hover:** Shows tooltip "Export model"
- **Click:** Opens format selection dropdown

---

## 12. Changing the Model

### Trigger:

User clicks the core engine block in the 3D scene, then selects "Change Model" from the context menu.

### Context Menu:

When the user clicks the core engine block:
- A small **context menu** appears next to the cursor
- Options:
  - "Change Model" — opens the model selector
  - "Model Info" — shows model details in a popup
  - "Reset Configuration" — resets all extensions to defaults

### Change Model Flow:

1. User clicks "Change Model"
2. A **confirmation dialog** appears: "Changing the model will reset all extension configurations. Continue?"
3. If confirmed:
   - The current 3D machine **dissolves** (particles fly outward, 0.5s)
   - The right panel opens with the model selector
   - User selects a new model
   - The new machine **assembles** (same as initial selection animation)

---

## 13. Responsive Behavior

### Desktop (>1024px):

- Full layout as described above
- Right panel: 320px wide
- Notebook window: 420px wide

### Tablet (768px - 1024px):

- Right panel: 280px wide
- Notebook window: 320px wide
- Info panel: Always collapsed (48px)

### Mobile (<768px):

- Right panel: Full width (slides up from bottom instead of right)
- Notebook window: Full width (slides up from bottom)
- Info panel: Hidden (accessed via swipe-up gesture)
- 3D scene: Full viewport, touch gestures for rotation/zoom
- Develop mode: Disabled (too complex for small screens)

---

## 14. Animations & Transitions Reference

| Element | Trigger | Animation | Duration | Easing |
|---------|---------|-----------|----------|--------|
| `+` button | Hover | Scale 1.0→1.1, border brightens | 0.2s | ease |
| `+` button | Model selected | Fade out | 0.2s | ease |
| Right panel | Open | Slide in from right | 0.3s | ease-out |
| Right panel | Close | Slide out to right | 0.2s | ease-in |
| Family card | Click | Expand height | 0.2s | ease |
| Version card | Click | Expand height | 0.2s | ease |
| Core engine | First appear | Fade in + scale 0.8→1.0 | 0.5s | ease-out |
| Core engine | Continuous | Slow Y rotation | continuous | linear |
| Extensions | First appear | Fly in from outside | 0.5s each, staggered | ease-out |
| Cables | First appear | Draw from core to extension | 0.3s each, staggered | ease-out |
| Extension | Click | Flash (opacity pulse) | 0.3s | ease |
| Extension | Hover | Brighten + tooltip | 0.2s | ease |
| Option card | Select | Border color change | 0.2s | ease |
| Notebook tab | Code change | Brief pulse | 0.5s | ease |
| Notebook window | Expand | Slide in from top-right | 0.3s | ease-out |
| Notebook window | Collapse | Slide out to top-right | 0.2s | ease-in |
| Code line | Update | Background flash | 0.5s | ease |
| Warning toast | Appear | Slide in from right | 0.3s | ease-out |
| Warning toast | Dismiss | Slide out to right | 0.2s | ease-in |
| Info panel | Expand | Height 48→120px | 0.2s | ease |
| Develop mode | Activate | 3D→flat transition | 0.5s | ease |
| Develop mode | Deactivate | Flat→3D transition | 0.5s | ease |
| Layer row | Remove | Height→0, opacity→0 | 0.2s | ease |
| 3D machine | Change model | Dissolve particles | 0.5s | ease-out |
| 3D machine | New model | Assemble particles | 0.5s | ease-out |

---

## 15. Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Esc` | Close any open panel (model selector, config, develop mode) |
| `Space` | Toggle notebook window |
| `D` | Toggle develop mode |
| `E` | Open export dropdown |
| `R` | Reset camera position |
| `1-7` | Select extension 1-7 (open config panel) |
| `Ctrl+Z` | Undo last action |
| `Ctrl+Shift+Z` | Redo last action |

---

## 16. Edge Cases & Error States

### No model definition found:

- **Cause:** API returns 404 for a model family/version
- **Display:** Error toast: "Model not found. Please try another." (red border)
- **Recovery:** Model selector stays open, user can pick another model

### Export fails:

- **Cause:** Backend error during notebook/YAML generation
- **Display:** Error toast: "Export failed. Please try again." (red border)
- **Recovery:** Download button stays enabled, user can retry

### Network offline:

- **Cause:** User loses internet connection
- **Display:** A subtle banner at the top: "Offline mode — all features available locally"
- **Behavior:** All features work (no API calls needed for the builder), export still works (client-side generation as fallback)

### Empty model (no layers):

- **Cause:** User removes all layers in develop mode
- **Display:** The 3D scene shows just the core engine block (no layers). The notebook shows only imports and an empty model class.
- **Warning:** "No layers defined. Add layers in Develop Mode."

### Maximum layers reached:

- **Cause:** User tries to add more than 50 layers
- **Display:** Warning toast: "Maximum 50 layers reached. Remove unused layers to add more."
- **Behavior:** Add Layer button becomes disabled

---

*Last updated: June 30, 2026*
*For questions, ask Hazem or Slofan.*
