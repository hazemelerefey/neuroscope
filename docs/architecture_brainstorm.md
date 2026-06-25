# NeuroScope — Architecture & Working Brainstorm

> How the tool will be built, how it works internally, and how it differs from modelviz-ai

---

## 1. HOW MODELVIZ-AI WORKS (What We Learned)

### Their Internal Architecture

```
modelviz/
├── parsers/
│   ├── torch_parser.py      ← Forward hooks on nn.Module
│   ├── tf_parser.py         ← Keras config JSON
│   └── fx_tracer.py         ← Skip connection detection (NEW, incomplete)
├── graph/
│   ├── layer_node.py        ← LayerNode dataclass
│   └── builder.py           ← Linear edges only (skip/branch TODO)
├── renderers/
│   ├── graphviz_renderer.py ← 2D static diagrams
│   ├── plotly_renderer.py   ← Basic 3D fallback
│   └── threejs_renderer.py  ← Interactive 3D HTML
└── utils/
    ├── framework_detect.py  ← Auto-detect PyTorch vs Keras
    └── grouping.py          ← Sliding window pattern matching
```

### How They Parse Models

**PyTorch (`torch_parser.py`):**
1. Register forward hooks on every leaf module (skip Sequential, ModuleList, etc.)
2. Create a dummy input tensor with the given shape
3. Run a forward pass with `torch.no_grad()`
4. Each hook captures: layer type, input shape, output shape, param count
5. Build LayerNode list in execution order
6. Remove hooks after

**Key limitation:** Requires the model object in memory (Python code). Can't parse a `.pt` file directly without loading it first.

### How They Build the Graph

**`builder.py`:**
- Simple linear edges: node[0] → node[1] → node[2] → ...
- Skip connections: **TODO (not implemented)**
- Transformer attention: **TODO (not implemented)**
- No branching, no residual detection

### How They Render 3D

**`threejs_renderer.py`:**
1. Classify each layer into a category (conv, linear, pool, activation, etc.)
2. Map category → 3D shape (box, plane, sphere, cylinder, etc.)
3. Map category → color (indigo, purple, cyan, etc.)
4. Calculate geometry dimensions from output shapes + param counts
5. Generate a standalone HTML file with embedded Three.js + data as JSON
6. Add hover tooltips, animated particles, legend

### How They Group Layers

**`grouping.py`:**
- Sliding window pattern matching against predefined patterns
- Patterns: Conv+BN+ReLU, Conv+ReLU, Linear+ReLU, Dense+Activation, etc.
- Merges matched nodes into a single LayerNode with combined info

### What They DON'T Do (Our Opportunity)

| Feature | modelviz-ai | NeuroScope |
|---------|-------------|------------|
| Input method | Python code only | **File upload (.onnx, .pt, .h5)** |
| Architecture analysis | ❌ None | ✅ **47+ anti-patterns** |
| FLOPs calculation | ❌ On roadmap | ✅ Per-layer + total |
| Memory estimation | ❌ None | ✅ Weights + optimizer + activations |
| Training time estimate | ❌ None | ✅ Hardware-aware |
| Skip connections | ❌ TODO | ✅ ONNX graph analysis |
| Model comparison | ❌ On roadmap | ✅ Side-by-side |
| Export 3D model | ❌ HTML only | ✅ GLB/GLTF |
| Export report | ❌ None | ✅ PDF + Markdown |
| Web app | ❌ Jupyter only | ✅ Browser-based |
| File upload | ❌ Needs code | ✅ Drag & drop |
| Educational explanations | ❌ None | ✅ Layer descriptions |
| Parameter simulation | ❌ None | ✅ Interactive sliders |
| Model cards | ❌ None | ✅ Auto-generated |
| Offline (PWA) | ❌ None | ✅ Planned |
| Multilingual | ❌ English only | ✅ FR, AR, SW, PT |

---

## 2. HOW NEUROSCOPE WORKS (Internal Design)

> **Implementation Status Legend:**
> - ✅ **Implemented** — working in the current codebase
> - 🚧 **In Development** — actively being built
> - 📋 **Planned** — designed but not started

### The Complete Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (React)                   │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Upload   │  │  3D Canvas   │  │  Analysis Panel        │ │
│  │  Zone     │  │  (Three.js)  │  │  (Linter Results)      │ │
│  └────┬─────┘  └──────▲───────┘  └────────────▲───────────┘ │
│       │               │                        │             │
└───────┼───────────────┼────────────────────────┼─────────────┘
        │               │                        │
        ▼               │                        │
┌───────────────────────┴────────────────────────┴─────────────┐
│                    BACKEND (FastAPI)                          │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │  PARSER   │───▶│ GRAPH    │───▶│ ANALYZER │               │
│  │  ENGINE   │    │ BUILDER  │    │ (LINTER) │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│       │                              │                       │
│       ▼                              ▼                       │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │  ONNX    │    │  SKIP    │    │  FLOPs   │               │
│  │  Parser  │    │  CONN    │    │  Memory  │               │
│  │  PyTorch │    │  Detect  │    │  Time    │               │
│  │  Keras   │    │          │    │  Est.    │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │           EXPORT ENGINE                   │               │
│  │  GLB (3D) │ SVG/PDF (Diagram) │ MD (Report) │            │
│  └──────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────┘
```

### Phase 1: Model Parsing (The Input Layer)

**NeuroScope's key difference:** Works with FILES, not code.

#### ONNX Parser (Primary — Universal Format) ✅ IMPLEMENTED
```python
# What ONNX gives us from the protobuf:
ModelProto
├── graph
│   ├── node[]          # Each operator: op_type, inputs, outputs, attributes
│   ├── input[]         # Model inputs with shapes
│   ├── output[]        # Model outputs with shapes
│   ├── initializer[]   # Weight tensors with shapes + data
│   └── value_info[]    # Intermediate tensor shapes
```

**How to parse:**
1. Load `.onnx` file with `onnx` library
2. Iterate `graph.node` → each node is a layer/operation
3. Extract `op_type` (Conv, Relu, MatMul, etc.)
4. Extract `attribute` (kernel_shape, strides, padding, etc.)
5. Extract weight shapes from `initializer`
6. Build connection graph from input/output tensor names
7. Calculate shapes by following the tensor flow

**Advantage over modelviz:** modelviz needs the Python model object. We just need the file.

#### PyTorch Parser (For .pt files) 🚧 IN DEVELOPMENT
```
.pt file → torch.load() → model object → torch.onnx.export() → ONNX → parse ONNX
```
Or use `torchinfo` to get summary directly.

#### Keras Parser (For .h5/.keras files) 🚧 IN DEVELOPMENT
```
.keras file → ZIP → config.json → parse JSON structure
.h5 file → h5py → model config → parse JSON structure
```

### Phase 2: Graph Construction (The Internal Model) ✅ IMPLEMENTED

**Unified Graph Format** — all parsers produce the same intermediate representation:

```python
@dataclass
class NeuroScopeNode:
    id: int
    name: str                    # e.g., "features.0.conv1"
    op_type: str                 # e.g., "Conv"
    category: str                # e.g., "convolution"
    input_shapes: list[list]     # [[1, 3, 224, 224]]
    output_shapes: list[list]    # [[1, 64, 112, 112]]
    attributes: dict             # {"kernel_shape": [7,7], "strides": [2,2]}
    params: int                  # 9408
    flops: int                   # 118013952
    memory_bytes: int            # 37632
    connections_in: list[int]    # [0]
    connections_out: list[int]   # [2, 3]
    is_grouped: bool
    grouped_types: list[str]

@dataclass
class NeuroScopeGraph:
    nodes: list[NeuroScopeNode]
    edges: list[Edge]            # source, target, type (sequential/skip/residual)
    input_shapes: list           # Model input shapes
    output_shapes: list          # Model output shapes
    total_params: int
    total_flops: int
    total_memory: int
    architecture_type: str       # "CNN", "Transformer", "RNN", "GAN", etc.
```

### Phase 3: Architecture Analysis (THE DIFFERENTIATOR) ✅ IMPLEMENTED

This is what makes NeuroScope unique. The analyzer takes the graph and runs a rules engine.

#### The Rules Engine

```
┌─────────────────────────────────────────┐
│            ANALYSIS PIPELINE            │
│                                         │
│  Input: NeuroScopeGraph                 │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Layer-Level Checks (4 rules) ✅ │   │
│  │  • Missing activation           │   │
│  │  • Sigmoid in deep networks     │   │
│  │  • BN placement                 │   │
│  │  • Activation after final layer │   │
│  └─────────────┬───────────────────┘   │
│                │                        │
│  ┌─────────────▼───────────────────┐   │
│  │  Architecture-Level (4 rules) ✅│   │
│  │  • No skip connections          │   │
│  │  • FC parameter explosion       │   │
│  │  • Missing dropout              │   │
│  │  • Premature flattening         │   │
│  └─────────────┬───────────────────┘   │
│                │                        │
│  ┌─────────────▼───────────────────┐   │
│  │  Efficiency Checks (3 rules) ✅ │   │
│  │  • Redundant convolutions       │   │
│  │  • Large kernels                │   │
│  │  • No pooling after conv        │   │
│  └─────────────┬───────────────────┘   │
│                │                        │
│  ┌─────────────▼───────────────────┐   │
│  │  Task-Specific (18 rules) 📋   │   │
│  │  • CNN/RNN/Transformer/GAN      │   │
│  │  • Planned, not yet implemented │   │
│  └─────────────┬───────────────────┘   │
│                │                        │
│  ┌─────────────▼───────────────────┐   │
│  │  Stats Calculator ✅            │   │
│  │  • FLOPs per layer + total      │   │
│  │  • Memory footprint             │   │
│  └─────────────┬───────────────────┘   │
│                │                        │
│                ▼                        │
│  Output: AnalysisReport                 │
│  • findings[] (severity, message, fix)  │
│  • stats (flops, memory)                │
└─────────────────────────────────────────┘
```

**Current rule count: 11 rules** (4 layer + 4 architecture + 3 efficiency)
**Planned: 18 additional task-specific rules** (CNN, RNN, Transformer, GAN anti-patterns)

#### Example Detection Logic

**Detect missing activation between linear layers:**
```python
def check_missing_activation(graph: NeuroScopeGraph) -> list[Finding]:
    findings = []
    linear_types = {"Linear", "Gemm", "MatMul", "Dense"}
    activation_types = {"Relu", "Gelu", "Sigmoid", "Tanh", "Softmax", ...}
    
    for i, node in enumerate(graph.nodes):
        if node.op_type in linear_types:
            # Check if next non-trivial node is also linear
            next_linear = find_next_linear(graph, i)
            if next_linear and not has_activation_between(graph, i, next_linear):
                findings.append(Finding(
                    severity="CRITICAL",
                    message=f"No activation between {node.name} and {next_linear.name}",
                    fix="Add ReLU, GELU, or other activation between linear layers",
                    layer_ids=[node.id, next_linear.id]
                ))
    return findings
```

**Detect vanishing gradient risk:**
```python
def check_vanishing_gradient(graph: NeuroScopeGraph) -> list[Finding]:
    findings = []
    depth = count_non_activation_layers(graph)
    has_skip = has_skip_connections(graph)
    uses_sigmoid_tanh = has_saturating_activations(graph)
    
    if depth > 10 and not has_skip:
        findings.append(Finding(
            severity="CRITICAL",
            message=f"Network has {depth} layers without skip connections",
            fix="Add residual connections or use architectures like ResNet",
            suggested_architecture="ResNet, DenseNet, or add skip connections"
        ))
    return findings
```

### Phase 4: 3D Visualization (The Visual Layer) ✅ IMPLEMENTED

**How it differs from modelviz:**

| Aspect | modelviz | NeuroScope |
|--------|----------|------------|
| Data source | Python model object | Parsed ONNX/graph data |
| Connection detection | Linear only | Sequential + skip + residual |
| Layer info | Type, shapes, params | Type, shapes, params, FLOPs, memory |
| Interaction | Hover only | Click + hover + select |
| Annotation | None | Layer descriptions + warnings |
| Comparison | None | 📋 Planned (side-by-side mode) |

**3D Shape Mapping (enhanced from modelviz):**

| Layer Type | Shape | Visual Meaning |
|------------|-------|----------------|
| Conv1d/2d/3d | 3D Box | Volume = channels × spatial |
| Linear/Dense | Flat Plane | 2D weight matrix |
| Pooling | Small Cube | Reduced spatial dims |
| Activation (ReLU, GELU) | Glowing Sphere | Uniform element-wise |
| BatchNorm/LayerNorm | Thin Slab | Normalization layer |
| Flatten | Cone | Funnels to 1D |
| Dropout | Wireframe | Sparse connections |
| LSTM/GRU | Cylinder | Recurrent flow |
| Multi-Head Attention | Octahedron | Multi-head pattern |
| Residual/Skip | Curved Arrow | Skip connection path |
| Concat | Merge Shape | Feature concatenation |
| Add | Plus Shape | Residual addition |

**Interactive Features (beyond modelviz):**
- Click a layer → detailed panel with params, FLOPs, memory, description
- Click a warning → highlight the problematic layers in 3D
- Filter by layer type (show only Conv, hide activations, etc.)
- Toggle skip connection visualization
- Step through forward pass animation
- Compare two models side by side

### Phase 5: Export (The Output Layer) 🚧 IN DEVELOPMENT

| Format | Content | Status |
|--------|---------|--------|
| **GLB/GLTF** | 3D model file importable into PowerPoint, Blender, web | 📋 Planned |
| **SVG** | 2D architecture diagram with annotations | 📋 Planned |
| **PDF** | Full analysis report with findings + stats | 🚧 Building |
| **Markdown** | Model summary for documentation | 🚧 Building |
| **HTML** | Standalone interactive 3D viewer | 📋 Planned |

---

## 3. TECHNICAL ARCHITECTURE (Component Map)

```
neuroscope/
├── backend/                          # Python FastAPI
│   ├── main.py                       # FastAPI app entry
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py             # POST /upload — receive model file
│   │   │   ├── analyze.py            # POST /analyze — run linter
│   │   │   ├── export.py             # POST /export — generate files
│   │   │   └── compare.py            # POST /compare — two models
│   │   └── models/
│   │       ├── graph.py              # NeuroScopeNode, NeuroScopeGraph
│   │       ├── findings.py           # Finding, AnalysisReport
│   │       └── stats.py              # FLOPs, Memory, TimeEstimate
│   ├── parsers/
│   │   ├── base.py                   # Abstract parser interface
│   │   ├── onnx_parser.py            # ONNX file parser (primary)
│   │   ├── pytorch_parser.py         # .pt → ONNX → parse
│   │   ├── keras_parser.py           # .h5/.keras → parse
│   │   └── tflite_parser.py          # .tflite → parse
│   ├── analysis/
│   │   ├── engine.py                 # Rules engine orchestrator
│   │   ├── rules/
│   │   │   ├── layer_rules.py        # Layer-level anti-patterns
│   │   │   ├── architecture_rules.py # Architecture-level anti-patterns
│   │   │   ├── efficiency_rules.py   # Efficiency anti-patterns
│   │   │   └── task_rules.py         # Task-specific rules
│   │   ├── flops.py                  # FLOPs calculator
│   │   ├── memory.py                 # Memory estimator
│   │   ├── training_time.py          # Training time estimator
│   │   └── model_card.py             # Auto model card generator
│   ├── graph/
│   │   ├── builder.py                # Build NeuroScopeGraph from parsed data
│   │   ├── skip_detector.py          # Detect skip/residual connections
│   │   ├── group.py                  # Layer pattern grouping
│   │   └── classifier.py             # Detect architecture type (CNN, etc.)
│   └── export/
│       ├── glb_exporter.py           # 3D model export
│       ├── svg_exporter.py           # 2D diagram export
│       ├── pdf_exporter.py           # Report export
│       └── markdown_exporter.py      # Markdown summary
│
├── frontend/                         # React + Three.js
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── UploadZone.tsx         # Drag & drop file upload
│   │   │   ├── Canvas3D.tsx           # Three.js 3D visualization
│   │   │   ├── LayerPanel.tsx         # Layer detail panel
│   │   │   ├── AnalysisPanel.tsx      # Linter results
│   │   │   ├── StatsPanel.tsx         # FLOPs, memory, time
│   │   │   ├── CompareView.tsx        # Side-by-side comparison
│   │   │   ├── ExportMenu.tsx         # Export options
│   │   │   └── ModelCard.tsx          # Auto-generated model card
│   │   ├── hooks/
│   │   │   ├── useModelUpload.ts      # File upload logic
│   │   │   ├── useThreeScene.ts       # Three.js scene management
│   │   │   └── useAnalysis.ts         # API calls for analysis
│   │   ├── three/
│   │   │   ├── shapes.ts              # Layer type → 3D geometry mapping
│   │   │   ├── colors.ts              # Layer type → color mapping
│   │   │   ├── layout.ts              # Node positioning algorithm
│   │   │   ├── edges.ts               # Connection rendering
│   │   │   └── animation.ts           # Forward pass animation
│   │   └── utils/
│   │       ├── api.ts                 # Backend API client
│   │       └── format.ts              # Number formatting
│   └── public/
│       └── index.html
│
├── samples/                          # Example model files for testing
│   ├── resnet18.onnx
│   ├── mobilenet_v2.onnx
│   ├── simple_cnn.onnx
│   └── lstm_example.onnx
│
├── tests/
│   ├── test_parsers/
│   │   ├── test_onnx_parser.py
│   │   ├── test_pytorch_parser.py
│   │   └── test_keras_parser.py
│   ├── test_analysis/
│   │   ├── test_layer_rules.py
│   │   ├── test_architecture_rules.py
│   │   ├── test_flops.py
│   │   └── test_memory.py
│   ├── test_graph/
│   │   ├── test_builder.py
│   │   └── test_skip_detector.py
│   └── test_export/
│       ├── test_glb_exporter.py
│       └── test_pdf_exporter.py
│
├── config/
│   ├── analysis_rules.yaml           # Rule definitions + thresholds
│   ├── layer_shapes.yaml             # Layer type → 3D shape mapping
│   ├── colors.yaml                   # Color scheme
│   └── languages/                    # i18n translations
│       ├── en.json
│       ├── fr.json
│       ├── ar.json
│       └── sw.json
│
├── competition/                      # Competition materials (already created)
├── docs/                             # Documentation
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── package.json
└── README.md
```

---

## 4. KEY TECHNICAL CHALLENGES & SOLUTIONS

### Challenge 1: ONNX Doesn't Have Direct Skip Connection Info

**Problem:** ONNX graph is a flat list of nodes. Skip connections are implicit (tensor names shared between nodes).

**Solution:**
```python
def detect_skip_connections(graph):
    # Build a tensor → producer mapping
    tensor_producers = {}
    for node in graph.nodes:
        for output in node.outputs:
            tensor_producers[output] = node.id
    
    # Find nodes that consume tensors from non-adjacent nodes
    for node in graph.nodes:
        for input_name in node.inputs:
            if input_name in tensor_producers:
                producer_id = tensor_producers[input_name]
                if abs(producer_id - node.id) > 2:  # Non-adjacent = skip
                    graph.add_edge(producer_id, node.id, edge_type="skip")
```

### Challenge 2: FLOPs Calculation from ONNX

**Problem:** Different ops have different FLOPs formulas.

**Solution:**
```python
FLOPS_FORMULAS = {
    "Conv": lambda attrs, inputs: (
        inputs[0] * inputs[1] *  # batch × channels_in
        attrs["kernel_shape"][0] * attrs["kernel_shape"][1] *  # kernel
        outputs[1] * outputs[2] * outputs[3]  # channels_out × spatial
    ),
    "MatMul": lambda attrs, inputs: inputs[0] * inputs[1] * inputs[2],
    "Gemm": lambda attrs, inputs: inputs[0] * inputs[1] * inputs[2],
    "BatchNormalization": lambda attrs, inputs: inputs[0] * inputs[1] * 4,
    # ... etc
}
```

### Challenge 3: Browser-Based ONNX Parsing (No Backend)

**Problem:** Heavy parsing should happen server-side, but basic visualization could work client-side.

**Solution:** Two modes:
- **Light mode (client-side):** Use `protobuf.js` to parse ONNX structure in browser. Basic 3D viz, no analysis.
- **Full mode (server-side):** Upload to FastAPI backend. Full analysis + FLOPs + memory + linter.

### Challenge 4: Large Models (1000+ layers)

**Problem:** Rendering 1000+ 3D objects is slow.

**Solution:**
- Layer grouping (merge Conv+BN+ReLU into one node)
- Level-of-detail (far away = simplified shapes)
- Frustum culling (don't render off-screen layers)
- Lazy loading (only render visible portion)

---

## 5. DEVELOPMENT PHASES

### Phase 1: Core Pipeline ✅ DONE
- ✅ ONNX parser → NeuroScopeGraph
- ✅ 3D visualization (Three.js)
- ✅ File upload endpoint
- ✅ Single model view

### Phase 2: Analysis Engine ✅ DONE
- ✅ Layer-level rules (4 rules)
- ✅ Architecture-level rules (4 rules)
- ✅ Efficiency rules (3 rules)
- ✅ FLOPs + memory calculation
- ✅ Analysis panel in UI

### Phase 3: Advanced Features 🚧 IN PROGRESS
- ✅ Skip connection detection (basic)
- 🚧 PyTorch + Keras parsers
- 🚧 Export (PDF, Markdown)
- 🚧 Model comparison mode

### Phase 4: Polish & Deploy 📋 PLANNED
- 📋 Forward pass animation
- 📋 Model card generation
- 📋 Multilingual support
- 📋 Deploy to cloud
- 📋 Demo video

---

## 6. WHAT MAKES NEUROSCOPE DIFFERENT (Summary)

| Dimension | modelviz-ai | Netron | NeuroScope |
|-----------|-------------|--------|------------|
| **Input** | Python code | Model file | Model file (drag & drop) |
| **Visualization** | 2D + 3D (Jupyter) | 2D only | 3D interactive (web) |
| **Analysis** | ❌ None | ❌ None | ✅ 11 rules (11 more planned) |
| **FLOPs** | ❌ On roadmap | ❌ None | ✅ Per-layer |
| **Memory** | ❌ None | ❌ None | ✅ Detailed |
| **Skip connections** | ❌ TODO | ✅ Shows edges | ✅ Detects + visualizes |
| **Comparison** | ❌ On roadmap | ❌ None | 🚧 Building |
| **Export** | HTML only | SVG/PNG | 🚧 PDF + MD (GLB/SVG planned) |
| **Education** | ❌ None | ❌ None | ✅ Layer explanations |
| **Deployment** | pip install | Desktop/web | Web app (any device) |
| **Offline** | N/A | Desktop only | 📋 Planned (PWA) |
| **Language** | English | English | English (multilingual planned) |

**One-line pitch:**
> "modelviz shows you what your model looks like. NeuroScope tells you what's wrong with it."
