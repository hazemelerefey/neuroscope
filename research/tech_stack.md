# NeuroScope — Technical Stack Research Report

**Date:** 2026-06-25  
**Purpose:** Comprehensive technical research for building a web-based neural network architecture visualizer  
**Target:** "NeuroScope" — an interactive 3D tool for visualizing, analyzing, and profiling neural network architectures from multiple frameworks

---

## Table of Contents

1. [ONNX Format & Python Parsing](#1-onnx-format--python-parsing)
2. [Three.js — 3D Rendering in Browser](#2-threejs--3d-rendering-in-browser)
3. [onnxruntime-web — Browser-based ONNX](#3-onnxruntime-web--browser-based-onnx)
4. [FastAPI — Python Backend](#4-fastapi--python-backend)
5. [React + Three.js (react-three-fiber)](#5-react--threejs-react-three-fiber)
6. [TensorFlow.js — Browser Model Parsing](#6tensorflowjs--browser-model-parsing)
7. [PyTorch Model Extraction](#7-pytorch-model-extraction)
8. [Keras Model Extraction](#8-keras-model-extraction)
9. [ONNX Layer Type Representation](#9-onnx-layer-type-representation)
10. [FLOPs Calculation from ONNX](#10-flops-calculation-from-onnx)
11. [Memory Footprint Estimation](#11-memory-footprint-estimation)
12. [Architecture Anti-pattern Detection](#12-architecture-anti-pattern-detection)
13. [Recommended Architecture & Integration](#13-recommended-architecture--integration)

---

## 1. ONNX Format & Python Parsing

### 1.1 Overview

| Property | Value |
|---|---|
| **Current Version** | ONNX 1.17.0 (onnx PyPI), spec version 1.23.0 (docs) |
| **License** | Apache-2.0 |
| **Maturity** | Production-grade, Linux Foundation project |
| **Maintainers** | Microsoft, Meta, AWS, Google, and community |
| **GitHub** | github.com/onnx/onnx (~17k stars) |
| **Python Package** | `pip install onnx` |
| **Python Support** | 3.9 – 3.13 |

### 1.2 ONNX Protobuf Schema — What's Available

ONNX uses Protocol Buffers (protobuf) as its serialization format. The core schema defines:

```
ModelProto
├── ir_version          # IR spec version (currently 10)
├── opset_import        # Operator set versions used
├── producer_name       # e.g., "pytorch", "tf2onnx"
├── producer_version
├── graph               # GraphProto
│   ├── node[]          # All operator nodes
│   │   ├── op_type     # e.g., "Conv", "Relu", "MatMul"
│   │   ├── input[]     # Input tensor names
│   │   ├── output[]    # Output tensor names
│   │   ├── attribute[] # Op-specific attributes (AttributeProto)
│   │   │   ├── name    # e.g., "kernel_shape", "strides"
│   │   │   ├── type    # INT, FLOAT, STRING, INTS, FLOATS, TENSOR
│   │   │   └── ints/f/floats/s/tensor
│   │   └── doc_string
│   ├── input[]         # Graph inputs (ValueInfoProto)
│   │   ├── name
│   │   ├── type        # TypeProto
│   │   │   ├── tensor_type
│   │   │   │   ├── elem_type  # FLOAT, INT64, etc. (TensorProto.DataType enum)
│   │   │   │   └── shape      # TensorShapeProto
│   │   │   │       └── dim[]  # dimensions (may have symbolic names)
│   │   │   ├── sequence_type
│   │   │   └── map_type
│   │   └── doc_string
│   ├── output[]        # Graph outputs (ValueInfoProto)
│   ├── initializer[]   # Weight tensors (TensorProto)
│   │   ├── name
│   │   ├── dims[]
│   │   ├── data_type
│   │   ├── raw_data    # Raw bytes of weights
│   │   └── float_data, int32_data, etc.
│   ├── sparse_initializer[]  # Sparse weights
│   └── name
├── metadata_props[]    # Key-value metadata
└── training_info       # Optional training metadata
```

**Key data extractable from ONNX:**
- **Full computation graph** — every node, its op_type, inputs, outputs, and attributes
- **Weight tensors** — all initializer data (shapes, values, data types)
- **Input/output shapes** — from ValueInfoProto, after shape inference
- **Symbolic dimensions** — batch_size, seq_len, etc. as string dim_params
- **Operator set versions** — which ONNX opset each domain uses
- **Metadata** — producer, version, custom properties

### 1.3 Python API for Parsing ONNX

```python
import onnx
from onnx import helper, TensorProto, shape_inference

# Load model
model = onnx.load("model.onnx")
graph = model.graph

# Basic model info
print(f"IR version: {model.ir_version}")
print(f"Opset: {[o.version for o in model.opset_import]}")
print(f"Producer: {model.producer_name} v{model.producer_version}")

# Iterate nodes
for node in graph.node:
    print(f"Op: {node.op_type}")
    print(f"  Inputs: {list(node.input)}")
    print(f"  Outputs: {list(node.output)}")
    for attr in node.attribute:
        print(f"  Attr: {attr.name} = ", end="")
        if attr.type == onnx.AttributeProto.INTS:
            print(list(attr.ints))
        elif attr.type == onnx.AttributeProto.INT:
            print(attr.i)
        elif attr.type == onnx.AttributeProto.FLOAT:
            print(attr.f)
        elif attr.type == onnx.AttributeProto.STRING:
            print(attr.s.decode())
        elif attr.type == onnx.AttributeProto.TENSOR:
            print(f"<tensor {attr.t.dims}>")

# Get graph inputs (model parameters, not initializers)
for inp in graph.input:
    shape = []
    for dim in inp.type.tensor_type.shape.dim:
        if dim.dim_param:
            shape.append(dim.dim_param)  # symbolic, e.g., "batch_size"
        else:
            shape.append(dim.dim_value)  # concrete
    print(f"Input: {inp.name}, shape={shape}")

# Get weight initializers
for init in graph.initializer:
    import numpy as np
    w = numpy_helper.to_array(init)
    print(f"Weight: {init.name}, shape={w.shape}, dtype={w.dtype}")

# Run shape inference (fills in missing output shapes)
model = shape_inference.infer_shapes(model)
inferred_graph = model.graph

# Validate model
onnx.checker.check_model(model)

# Use helper to extract node attributes programmatically
for node in graph.node:
    attrs = helper.get_attribute_value(node)  # or iterate node.attribute
```

### 1.4 Advanced ONNX Tools

#### onnx-tool (Recommended for Profiling)

| Property | Value |
|---|---|
| **Version** | 1.0.1 (Apr 2026) |
| **License** | MIT |
| **GitHub** | ThanatosShinji/onnx-tool |
| **Key Features** | Shape inference, MACs/FLOPs counting, graph fusion, memory profiling |

```python
import onnx_tool
from onnx_tool import Model

# Profile a model — get MACs, params, memory
model = onnx_tool.Model("model.onnx")
model.profile()  # prints per-layer MACs and parameter counts
model.graph()    # prints graph structure

# Get shape inference
model.shape_infer()  # fast shape inference

# Export profiled data
model.save_model("profiled.onnx")
```

**Supported architectures:** BERT, GPT, LLaMA, T5, Stable Diffusion, YOLO, Mask R-CNN, ConvNeXt, and more.

#### onnx.compose — Model Surgery

```python
from onnx import compose

# Merge two models
merged = compose.merge_models(model_a, model_b, io_map=[("a_output", "b_input")])

# Extract subgraph
subgraph = compose.extract_model(
    model, 
    inputs=["input_name"],
    outputs=["intermediate_output"]
)
```

### 1.5 Limitations

- **Dynamic shapes** — symbolic dims need special handling; not all tools support them
- **Custom ops** — non-standard operators from specific frameworks may not parse
- **Large models** — multi-GB models can be slow to load; consider streaming
- **Subgraph operators** — Loop, If, Scan nodes contain nested graphs that need recursive traversal
- **External data** — weights >2GB stored in separate files; need `onnx.load_model(path, load_external_data=True)`

### 1.6 Alternatives

| Tool | Use Case | Notes |
|---|---|---|
| **Netron** | Visual inspection (standalone) | Web/desktop app, read-only |
| **onnxmltools** | Multi-framework conversion | Converts sklearn, lightgbm to ONNX |
| **onnxconverter-common** | Type handling during conversion | Microsoft maintained |
| **onnxsimplifier** | Graph simplification | Folds constants, removes redundant nodes |

---

## 2. Three.js — 3D Rendering in Browser

### 2.1 Overview

| Property | Value |
|---|---|
| **Current Version** | r175+ (2025–2026, semantic versioning since r160) |
| **License** | MIT |
| **GitHub** | mrdoob/three.js (~103k stars) |
| **npm** | `npm install three` |
| **Bundle Size** | ~600KB minified (tree-shakeable) |
| **Browser Support** | All modern browsers (WebGL 2.0, WebGPU experimental) |

### 2.2 Core Patterns for NeuroScope

#### Scene Setup with Different Shapes per Layer Type

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Orbit controls for navigation
const controls = new OrbitControls(camera, renderer.domElement);

// Layer type → geometry mapping
const geometryMap = {
  'Conv': () => new THREE.BoxGeometry(1, 1, 1),
  'ConvTranspose': () => new THREE.BoxGeometry(1, 1, 1),
  'MaxPool': () => new THREE.BoxGeometry(0.8, 0.8, 0.8),
  'AveragePool': () => new THREE.BoxGeometry(0.8, 0.8, 0.8),
  'Relu': () => new THREE.SphereGeometry(0.5, 32, 32),
  'Sigmoid': () => new THREE.SphereGeometry(0.5, 32, 32),
  'Tanh': () => new THREE.SphereGeometry(0.5, 32, 32),
  'Gemm': () => new THREE.CylinderGeometry(0.5, 0.5, 1, 6),  // hexagon for FC
  'MatMul': () => new THREE.CylinderGeometry(0.5, 0.5, 1, 6),
  'BatchNormalization': () => new THREE.TorusGeometry(0.4, 0.1, 16, 32),
  'Add': () => new THREE.OctahedronGeometry(0.4),  // merge/residual
  'Concat': () => new THREE.OctahedronGeometry(0.5),
  'Reshape': () => new THREE.TetrahedronGeometry(0.4),
  'Softmax': () => new THREE.ConeGeometry(0.4, 0.8, 32),
  'Dropout': () => new THREE.DodecahedronGeometry(0.3),
  'LSTM': () => new THREE.TorusKnotGeometry(0.3, 0.1, 64, 8),
  'Attention': () => new THREE.IcosahedronGeometry(0.5),
  'default': () => new THREE.BoxGeometry(0.6, 0.6, 0.6),
};

// Color mapping by layer category
const colorMap = {
  'convolution': 0x4285f4,   // blue
  'pooling': 0x34a853,       // green
  'activation': 0xfbbc05,    // yellow
  'normalization': 0xea4335, // red
  'linear': 0x9c27b0,        // purple
  'recurrent': 0xff6d00,     // orange
  'attention': 0x00bcd4,     // cyan
  'elementwise': 0x795548,   // brown
  'default': 0x9e9e9e,       // grey
};

function createLayerNode(layerInfo) {
  const geometryFactory = geometryMap[layerInfo.op_type] || geometryMap['default'];
  const material = new THREE.MeshPhongMaterial({
    color: colorMap[layerInfo.category] || colorMap['default'],
    transparent: true,
    opacity: 0.85,
  });
  const mesh = new THREE.Mesh(geometryFactory(), material);
  
  // Store metadata for click handling
  mesh.userData = {
    layerName: layerInfo.name,
    opType: layerInfo.op_type,
    inputShapes: layerInfo.input_shapes,
    outputShapes: layerInfo.output_shapes,
    params: layerInfo.param_count,
    flops: layerInfo.flops,
  };
  
  return mesh;
}
```

#### Click Events with Raycaster

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onMouseClick(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(layerNodes, true);
  
  if (intersects.length > 0) {
    const selected = intersects[0].object;
    showLayerDetails(selected.userData);
    highlightLayer(selected);
  }
}

function highlightLayer(mesh) {
  // Reset previous
  if (highlightedLayer) {
    highlightedLayer.material.emissive.setHex(0x000000);
  }
  // Highlight new
  mesh.material.emissive.setHex(0x333333);
  highlightedLayer = mesh;
}

window.addEventListener('click', onMouseClick, false);

// Hover effects
function onMouseMove(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(layerNodes);
  
  document.body.style.cursor = intersects.length > 0 ? 'pointer' : 'default';
}
window.addEventListener('mousemove', onMouseMove, false);
```

#### Animating Data Flow Between Layers

```javascript
// Animated connection lines (data flow)
function createDataFlowConnection(sourcePos, targetPos) {
  const curve = new THREE.QuadraticBezierCurve3(
    sourcePos,
    new THREE.Vector3(
      (sourcePos.x + targetPos.x) / 2,
      (sourcePos.y + targetPos.y) / 2 + 0.5,
      (sourcePos.z + targetPos.z) / 2
    ),
    targetPos
  );
  
  const points = curve.getPoints(50);
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({ color: 0x00ffff, opacity: 0.6, transparent: true });
  return new THREE.Line(geometry, material);
}

// Particle flow animation along connections
class DataFlowParticles {
  constructor(curve, count = 20) {
    this.curve = curve;
    this.particles = [];
    this.speed = 0.002;
    
    const geometry = new THREE.SphereGeometry(0.03, 8, 8);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
    
    for (let i = 0; i < count; i++) {
      const particle = new THREE.Mesh(geometry, material);
      particle.userData.t = i / count;  // stagger along curve
      this.particles.push(particle);
    }
  }
  
  update() {
    for (const p of this.particles) {
      p.userData.t = (p.userData.t + this.speed) % 1;
      const pos = this.curve.getPointAt(p.userData.t);
      p.position.copy(pos);
    }
  }
}

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  particleSystems.forEach(ps => ps.update());
  controls.update();
  renderer.render(scene, camera);
}
animate();
```

#### Export as GLB/GLTF

```javascript
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';

function exportScene() {
  const exporter = new GLTFExporter();
  exporter.parse(
    scene,
    (glb) => {
      const blob = new Blob([glb], { type: 'application/octet-stream' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'neuroscope_model.glb';
      a.click();
    },
    (error) => console.error('Export failed:', error),
    { binary: true }  // GLB format
  );
}
```

### 2.3 Performance Considerations

| Concern | Solution |
|---|---|
| **Many nodes (>1000)** | Use `THREE.InstancedMesh` for identical geometries |
| **Complex connections** | Use `THREE.BufferGeometry` with pre-computed line segments |
| **Interaction lag** | Use spatial indexing (octree) for raycaster |
| **Memory** | Dispose geometries/materials when switching models |
| **Mobile** | Reduce polygon count, use simpler materials |

### 2.4 Limitations

- **WebGL context limits** — max ~16 WebGL contexts per page (use single canvas)
- **No native SVG export** — need custom renderer or html2canvas
- **Large models** — 3D scene with >5k nodes needs LOD or grouping
- **Text rendering** — use CSS2DRenderer or SpriteText for labels
- **WebGPU** — experimental backend in Three.js r165+, not production-ready yet

### 2.5 Alternatives

| Tool | Use Case |
|---|---|
| **Babylon.js** | Game-oriented 3D, heavier but more built-in features |
| **Deck.gl** | Large-scale data visualization (WebGL2) |
| **Cytoscape.js** | 2D graph visualization (good for simpler views) |
| **D3.js + WebGL** | Custom data-driven visualization |
| **A-Frame** | VR/AR visualization of neural networks |

---

## 3. onnxruntime-web — Browser-based ONNX

### 3.1 Overview

| Property | Value |
|---|---|
| **Current Version** | 1.21.x (2025–2026) |
| **License** | MIT |
| **npm** | `npm install onnxruntime-web` |
| **Bundle Size** | ~2–5MB (WASM backend), ~3MB (WebGPU) |
| **Backends** | WASM, WASM SIMD, WASM Threads, WebGPU, WebGL |
| **Browser Support** | Chrome 91+, Firefox 89+, Safari 16.4+, Edge 91+ |

### 3.2 Key Features

- **In-browser inference** — run ONNX models without server round-trips
- **WebGPU backend** — GPU-accelerated inference (Chrome 113+)
- **WASM SIMD** — CPU SIMD acceleration via WebAssembly
- **WASM Threads** — multi-threaded inference (requires COOP/COEP headers)
- **Model quantization** — supports INT8/INT4 quantized models
- **Streaming** — supports model loading from URL without full download first

### 3.3 Code Example — Inference in Browser

```javascript
import * as ort from 'onnxruntime-web';

// Configure backend (WebGPU preferred, fallback to WASM)
ort.env.wasm.numThreads = navigator.hardwareConcurrency;
ort.env.wasm.proxy = true;  // run in worker

async function runInference(modelUrl, inputData) {
  // Create session — loads model
  const session = await ort.InferenceSession.create(modelUrl, {
    executionProviders: ['webgpu', 'wasm'],  // prefer WebGPU
    graphOptimizationLevel: 'all',
  });
  
  // Prepare input tensor
  const inputTensor = new ort.Tensor('float32', inputData, [1, 3, 224, 224]);
  
  // Run inference
  const results = await session.run({ input: inputTensor });
  
  // Access output
  const output = results.output.data;  // Float32Array
  console.log('Output shape:', results.output.dims);
  
  return output;
}
```

### 3.4 Can We Parse ONNX Files Client-Side Without a Backend?

**Partially — but with significant limitations.**

onnxruntime-web is designed for **inference**, not **graph parsing/analysis**. It can:
- ✅ Load and run ONNX models
- ✅ Get input/output names and shapes from session
- ❌ Extract full graph topology (nodes, connections, attributes)
- ❌ Access weight values or intermediate tensors
- ❌ List all layers and their configurations

**Client-side parsing alternatives:**

1. **protobuf.js** — Parse ONNX protobuf directly in JavaScript:
   ```javascript
   import protobuf from 'protobufjs';
   
   // Load ONNX proto definition (from onnx source)
   const root = await protobuf.load('onnx.proto');
   const ModelProto = root.lookupType('onnx.ModelProto');
   
   // Decode .onnx file
   const response = await fetch('model.onnx');
   const buffer = await response.arrayBuffer();
   const model = ModelProto.decode(new Uint8Array(buffer));
   
   // Access graph
   const graph = model.graph;
   graph.node.forEach(node => {
     console.log(node.opType, node.input, node.output);
   });
   ```

2. **onnx-proto npm package** — Pre-compiled ONNX protobuf definitions for JS

3. **Recommended approach:** Use backend (FastAPI) for heavy parsing, send lightweight JSON graph to frontend. Client-side parsing is feasible but fragile with large models.

### 3.5 Limitations

- **Memory** — models must fit in browser memory (~2GB practical limit)
- **Startup latency** — WASM initialization takes 1-3 seconds
- **Not all ops supported** — some ONNX ops lack WASM/WebGPU implementations
- **No training** — inference only
- **COOP/COEP headers** — required for WASM threads (limits embedding in iframes)

---

## 4. FastAPI — Python Backend

### 4.1 Overview

| Property | Value |
|---|---|
| **Current Version** | 0.138.0 (Jun 2026) |
| **License** | MIT |
| **Python** | 3.10 – 3.14 |
| **GitHub** | fastapi/fastapi (~82k stars) |
| **Status** | Beta (4 - Beta), production-proven |
| **Framework** | Built on Starlette + Pydantic v2 |

### 4.2 Key Features for NeuroScope

- **Async** — native async/await for non-blocking model parsing
- **Pydantic v2** — type-safe request/response schemas
- **File upload** — multipart form data for model files
- **CORS middleware** — for frontend-backend communication
- **WebSocket** — for real-time progress updates during parsing
- **Background tasks** — for long-running model analysis
- **OpenAPI/Swagger** — auto-generated API documentation

### 4.3 API Design for NeuroScope

```python
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import onnx
from onnx import numpy_helper, shape_inference
import tempfile, os, hashlib
from typing import Optional

app = FastAPI(title="NeuroScope API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Data Models ----

class LayerInfo(BaseModel):
    name: str
    op_type: str
    category: str  # convolution, activation, normalization, etc.
    inputs: list[str]
    outputs: list[str]
    attributes: dict
    input_shapes: list[list[int | str]]
    output_shapes: list[list[int | str]]
    param_count: int
    flops: int

class ModelInfo(BaseModel):
    name: str
    format: str  # onnx, keras, pytorch
    ir_version: int
    opset_versions: dict[str, int]
    producer: str
    layers: list[LayerInfo]
    total_params: int
    total_flops: int
    input_info: list[dict]
    output_info: list[dict]
    graph_edges: list[tuple[str, str]]  # (source_output, target_input)

class MemoryEstimate(BaseModel):
    weights_fp32: int  # bytes
    weights_fp16: int
    activations: int   # estimated
    peak_memory: int

class AntiPattern(BaseModel):
    type: str  # e.g., "redundant_reshape", "unnecessary_cast"
    severity: str  # "warning", "info"
    location: str  # node name
    description: str
    suggestion: str

# ---- Endpoints ----

@app.post("/api/parse", response_model=ModelInfo)
async def parse_model(file: UploadFile = File(...)):
    """Parse uploaded ONNX model and return architecture graph."""
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        model = onnx.load(tmp_path)
        model = shape_inference.infer_shapes(model)
        graph = model.graph
        
        layers = []
        for node in graph.node:
            layer = extract_layer_info(node, graph)
            layers.append(layer)
        
        edges = build_edges(graph)
        
        return ModelInfo(
            name=file.filename,
            format="onnx",
            ir_version=model.ir_version,
            opset_versions={o.domain or "ai.onnx": o.version for o in model.opset_import},
            producer=model.producer_name,
            layers=layers,
            total_params=sum(l.param_count for l in layers),
            total_flops=sum(l.flops for l in layers),
            input_info=get_input_info(graph),
            output_info=get_output_info(graph),
            graph_edges=edges,
        )
    finally:
        os.unlink(tmp_path)

@app.post("/api/memory-estimate", response_model=MemoryEstimate)
async def estimate_memory(file: UploadFile = File(...)):
    """Estimate memory footprint of the model."""
    # ... parse and estimate
    pass

@app.post("/api/anti-patterns", response_model=list[AntiPattern])
async def detect_anti_patterns(file: UploadFile = File(...)):
    """Detect architecture anti-patterns."""
    # ... analyze and report
    pass

@app.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    """Real-time progress for large model parsing."""
    await websocket.accept()
    # Send progress updates during long operations
    pass
```

### 4.4 Production Deployment

```bash
# With uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With Docker
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.5 Limitations

- **File size** — multipart upload has practical limits (~100MB default in most setups)
- **Memory** — large models (>1GB) can consume significant RAM during parsing
- **Sync blocking** — ONNX parsing is CPU-bound; use `run_in_executor` for truly async behavior
- **Streaming upload** — for very large models, consider chunked upload + websocket

### 4.6 Alternatives

| Framework | Notes |
|---|---|
| **Flask** | Simpler, less performant, no native async |
| **Starlette** | FastAPI's foundation, lower-level |
| **Litestar** | FastAPI alternative with different API style |
| **Gradio** | Quick demos but less control |

---

## 5. React + Three.js (react-three-fiber)

### 5.1 Overview

| Property | Value |
|---|---|
| **@react-three/fiber** | v9.x (2025–2026) |
| **@react-three/drei** | v10.x (helper components) |
| **License** | MIT |
| **GitHub** | pmndrs/react-three-fiber (~28k stars) |
| **npm** | `npm install @react-three/fiber @react-three/drei three` |

### 5.2 Integration Pattern

```tsx
// NeuroScope 3D Canvas Component
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Html, Environment, GizmoHelper } from '@react-three/drei';
import * as THREE from 'three';
import { useRef, useState, useMemo } from 'react';

// Individual layer node component
function LayerNode({ layer, position, onSelect }: {
  layer: LayerInfo;
  position: [number, number, number];
  onSelect: (layer: LayerInfo) => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  
  const geometry = useMemo(() => getGeometryForOpType(layer.op_type), [layer.op_type]);
  const color = useMemo(() => getColorForCategory(layer.category), [layer.category]);
  
  useFrame((state) => {
    if (meshRef.current && hovered) {
      meshRef.current.rotation.y += 0.01;
    }
  });
  
  return (
    <mesh
      ref={meshRef}
      position={position}
      geometry={geometry}
      onClick={(e) => { e.stopPropagation(); onSelect(layer); }}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <meshPhongMaterial 
        color={color} 
        emissive={hovered ? '#333' : '#000'} 
        transparent 
        opacity={0.85} 
      />
      {hovered && (
        <Html distanceFactor={10}>
          <div className="layer-tooltip">
            <strong>{layer.name}</strong>
            <br />Type: {layer.op_type}
            <br />Params: {formatNumber(layer.param_count)}
          </div>
        </Html>
      )}
    </mesh>
  );
}

// Connection line between layers
function Connection({ start, end }: { start: THREE.Vector3; end: THREE.Vector3 }) {
  const lineRef = useRef<THREE.Line>(null);
  const curve = useMemo(() => {
    return new THREE.QuadraticBezierCurve3(
      start,
      new THREE.Vector3(
        (start.x + end.x) / 2,
        Math.max(start.y, end.y) + 1,
        (start.z + end.z) / 2
      ),
      end
    );
  }, [start, end]);
  
  const points = useMemo(() => curve.getPoints(50), [curve]);
  
  return (
    <line ref={lineRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={points.length}
          array={new Float32Array(points.flatMap(p => [p.x, p.y, p.z]))}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial color="#00bcd4" opacity={0.4} transparent />
    </line>
  );
}

// Main 3D visualization canvas
function ModelVisualization({ modelData, onLayerSelect }: Props) {
  const positions = useMemo(() => computeLayout(modelData.layers), [modelData.layers]);
  
  return (
    <Canvas camera={{ position: [0, 0, 20], fov: 60 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <OrbitControls />
      
      {modelData.layers.map((layer, i) => (
        <LayerNode
          key={layer.name}
          layer={layer}
          position={positions[i]}
          onSelect={onLayerSelect}
        />
      ))}
      
      {modelData.graph_edges.map(([src, tgt], i) => {
        const srcPos = positions[getLayerIndex(src)];
        const tgtPos = positions[getLayerIndex(tgt)];
        return <Connection key={i} start={srcPos} end={tgtPos} />;
      })}
      
      <GizmoHelper alignment="bottom-right" margin={[60, 60]} />
    </Canvas>
  );
}

// App shell
function NeuroScopeApp() {
  const [modelData, setModelData] = useState(null);
  const [selectedLayer, setSelectedLayer] = useState(null);
  
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ flex: 1 }}>
        {modelData && (
          <ModelVisualization 
            modelData={modelData} 
            onLayerSelect={setSelectedLayer} 
          />
        )}
      </div>
      {selectedLayer && (
        <LayerDetailsPanel layer={selectedLayer} />
      )}
    </div>
  );
}
```

### 5.3 Key drei Components for NeuroScope

| Component | Use Case |
|---|---|
| `OrbitControls` | Camera navigation |
| `Html` | Layer info tooltips in 3D |
| `Text` | 3D text labels |
| `Line` | Connection lines between layers |
| `GizmoHelper` | Orientation widget |
| `Environment` | Lighting presets |
| `Bvh` | Performance: BVH-accelerated raycasting |
| `Points` | Particle effects for data flow |

### 5.4 Limitations

- **Reconciliation overhead** — React re-renders can be expensive with many 3D objects
- **Bundle size** — drei adds ~200KB, fiber ~100KB
- **Learning curve** — JSX ≠ Three.js; some Three.js concepts don't translate directly
- **SSR** — Three.js needs `useEffect` or dynamic import (no server-side 3D)

---

## 6. TensorFlow.js — Browser Model Parsing

### 6.1 Overview

| Property | Value |
|---|---|
| **Current Version** | 4.x (2025–2026) |
| **License** | Apache-2.0 |
| **npm** | `npm install @tensorflow/tfjs` |
| **Bundle Size** | ~1MB (core), ~3MB (with backends) |
| **Backends** | WebGL, WebGPU, WASM, CPU |

### 6.2 Supported Formats

| Format | Extension | Parsing | Inference |
|---|---|---|---|
| TF SavedModel | `.pb` (directory) | Via converter | ✅ |
| TF Lite | `.tflite` | Via tfjs-tflite | ✅ |
| Keras | `.h5`, `.keras` | Via converter | ✅ |
| TF Hub | URL | Via converter | ✅ |
| ONNX | — | ❌ Not supported | — |

### 6.3 Loading Models in Browser

```javascript
import * as tf from '@tensorflow/tfjs';

// Load TF.js model (layers format from .h5 conversion)
const model = await tf.loadLayersModel('/models/model.json');

// Load graph model (from SavedModel/PB conversion)
const graphModel = await tf.loadGraphModel('/models/model.json');

// Inspect architecture
console.log('Inputs:', model.inputs.map(i => ({
  name: i.name,
  shape: i.shape,
  dtype: i.dtype,
})));

console.log('Outputs:', model.outputs.map(o => ({
  name: o.name,
  shape: o.shape,
})));

// Layer-by-layer inspection
model.layers.forEach(layer => {
  console.log({
    name: layer.name,
    className: layer.getClassName(),
    inputShape: layer.inputSpec?.shape,
    outputShape: layer.outputSpec?.shape,
    params: layer.countParams(),
    config: layer.getConfig(),
  });
});

// TFLite via tfjs-tflite
import '@tensorflow/tfjs-tflite';
const tfliteModel = await tflite.loadTFLiteModel('/models/model.tflite');
```

### 6.4 Converting Models for Browser Use

```bash
# Convert Keras .h5 to TF.js format
tensorflowjs_converter \
  --input_format=keras \
  --output_format=tfjs_layers_model \
  model.h5 \
  tfjs_model/

# Convert SavedModel to TF.js
tensorflowjs_converter \
  --input_format=tf_saved_model \
  --output_format=tfjs_graph_model \
  saved_model_dir/ \
  tfjs_model/

# Convert TFLite to TF.js
tensorflowjs_converter \
  --input_format=tf_lite \
  --output_format=tfjs_graph_model \
  model.tflite \
  tfjs_model/
```

### 6.5 Limitations

- **No ONNX support** — cannot parse .onnx files
- **Conversion required** — models must be pre-converted to TF.js format
- **Op coverage** — not all TF ops have JS implementations
- **Large models** — need to split into shards for browser loading
- **.pb parsing** — cannot read raw protobuf .pb files; needs conversion

---

## 7. PyTorch Model Extraction

### 7.1 Overview

PyTorch models (`.pt`, `.pth`) are Python pickled objects. Extracting architecture requires either loading the model class or using summary tools.

### 7.2 Tools

#### torchinfo (Recommended)

| Property | Value |
|---|---|
| **Version** | 1.8.x |
| **pip** | `pip install torchinfo` |
| **GitHub** | TylerYep/torchinfo (~3k stars) |

```python
import torch
from torchinfo import summary

# Load model
model = torch.load("model.pt", map_location="cpu", weights_only=False)
model.eval()

# Get detailed summary
stats = summary(
    model,
    input_size=(1, 3, 224, 224),  # batch, channels, H, W
    col_names=["input_size", "output_size", "num_params", "mult_adds"],
    depth=5,  # nesting depth
    row_settings=["var_names"],
)

# Access structured data
print(f"Total params: {stats.total_params:,}")
print(f"Trainable params: {stats.trainable_params:,}")
print(f"Mult-Adds: {stats.total_mult_adds:,}")

# Per-layer info
for layer in stats.summary_list:
    print(f"{layer.var_name}: {layer.class_name}")
    print(f"  Input: {layer.input_size}")
    print(f"  Output: {layer.output_size}")
    print(f"  Params: {layer.num_params}")
    print(f"  MACs: {layer.macs}")
```

#### torchsummary (Legacy)

```python
from torchsummary import summary
summary(model, (3, 224, 224))
```

#### Manual Architecture Extraction

```python
import torch
import torch.nn as nn

def extract_pytorch_architecture(model, prefix=""):
    """Recursively extract PyTorch model architecture."""
    layers = []
    for name, module in model.named_children():
        full_name = f"{prefix}.{name}" if prefix else name
        layer_info = {
            "name": full_name,
            "type": type(module).__name__,
            "params": sum(p.numel() for p in module.parameters()),
            "trainable_params": sum(p.numel() for p in module.parameters() if p.requires_grad),
        }
        
        # Extract specific attributes
        if isinstance(module, nn.Conv2d):
            layer_info.update({
                "in_channels": module.in_channels,
                "out_channels": module.out_channels,
                "kernel_size": module.kernel_size,
                "stride": module.stride,
                "padding": module.padding,
                "groups": module.groups,
            })
        elif isinstance(module, nn.Linear):
            layer_info.update({
                "in_features": module.in_features,
                "out_features": module.out_features,
            })
        elif isinstance(module, nn.LSTM):
            layer_info.update({
                "input_size": module.input_size,
                "hidden_size": module.hidden_size,
                "num_layers": module.num_layers,
                "bidirectional": module.bidirectional,
            })
        elif isinstance(module, nn.MultiheadAttention):
            layer_info.update({
                "embed_dim": module.embed_dim,
                "num_heads": module.num_heads,
            })
        
        # Recurse into children
        children = extract_pytorch_architecture(module, full_name)
        layers.append(layer_info)
        layers.extend(children)
    
    return layers
```

### 7.3 Best Approach for NeuroScope

**Recommended workflow:**
1. Load `.pt` file server-side with PyTorch
2. Extract architecture via `torchinfo` or manual traversal
3. Convert to ONNX with `torch.onnx.export()` for unified format
4. Use ONNX parser as the single source of truth

```python
import torch

# Load and convert to ONNX
model = torch.load("model.pt", weights_only=False)
model.eval()
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model, dummy_input, "model.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    opset_version=17,
)
# Now parse with onnx library
```

### 7.4 Limitations

- **Requires model class** — `torch.load` needs the model class definition available
- **Pickle security** — `.pt` files can execute arbitrary code; use `weights_only=True` when possible
- **Custom layers** — custom `nn.Module` subclasses need manual handling
- **Dynamic models** — models with control flow (if/loop) are hard to trace

---

## 8. Keras Model Extraction

### 8.1 Overview

Keras models (`.h5`, `.keras`) store architecture config in JSON format, making extraction straightforward.

### 8.2 Extraction Methods

#### From .keras format (Keras 3.x)

```python
import keras

model = keras.saving.load_model("model.keras")

# Get full config (JSON-serializable)
config = model.get_config()

# Config structure:
# {
#   "name": "sequential",
#   "layers": [
#     {
#       "class_name": "Conv2D",
#       "config": {
#         "name": "conv2d",
#         "trainable": true,
#         "dtype": "float32",
#         "filters": 32,
#         "kernel_size": [3, 3],
#         "strides": [1, 1],
#         "padding": "valid",
#         "activation": "relu",
#         "input_shape": [null, 28, 28, 1],
#         ...
#       }
#     },
#     ...
#   ]
# }

# Per-layer extraction
for layer in model.layers:
    print(f"Layer: {layer.name} ({type(layer).__name__})")
    print(f"  Input shape: {layer.input_shape}")
    print(f"  Output shape: {layer.output_shape}")
    print(f"  Params: {layer.count_params()}")
    print(f"  Config: {layer.get_config()}")
```

#### From .h5 format (Keras 2.x)

```python
import h5py
import json

# Method 1: Via Keras (requires tf.keras)
from tensorflow import keras
model = keras.models.load_model("model.h5")
config = model.get_config()

# Method 2: Direct HDF5 reading (no TF dependency)
with h5py.File("model.h5", "r") as f:
    # Model config is stored as JSON string
    model_config = json.loads(f.attrs["model_config"])
    
    # Weights per layer
    for layer_name in f["model_weights"]:
        layer_group = f["model_weights"][layer_name]
        for var_name in layer_group:
            weight = layer_group[var_name]
            print(f"{layer_name}/{var_name}: shape={weight.shape}")

# Method 3: JSON config extraction without loading model
def extract_h5_config(path):
    with h5py.File(path, "r") as f:
        config = json.loads(f.attrs["model_config"])
    return config
```

#### Training config (from .keras)

```python
# .keras files are ZIP archives containing config.json + weights
import zipfile, json

with zipfile.ZipFile("model.keras", "r") as z:
    config = json.loads(z.read("config.json"))
    # Also contains: weights.h5 or model.weights.h5
```

### 8.3 Best Approach for NeuroScope

```python
def extract_keras_architecture(model_path: str) -> dict:
    """Extract architecture from Keras model."""
    if model_path.endswith(".keras"):
        model = keras.saving.load_model(model_path)
    elif model_path.endswith(".h5"):
        model = keras.models.load_model(model_path)
    else:
        raise ValueError(f"Unsupported format: {model_path}")
    
    layers = []
    for layer in model.layers:
        layer_config = layer.get_config()
        layers.append({
            "name": layer.name,
            "class_name": type(layer).__name__,
            "input_shape": str(layer.input_shape),
            "output_shape": str(layer.output_shape),
            "param_count": layer.count_params(),
            "config": layer_config,
            "trainable": layer.trainable,
        })
    
    return {
        "name": model.name,
        "total_params": model.count_params(),
        "layers": layers,
        "input_shape": str(model.input_shape),
        "output_shape": str(model.output_shape),
    }
```

### 8.4 Limitations

- **Keras 2 vs 3** — config format differs; Keras 3 uses different layer class names
- **Custom layers** — need class definitions to deserialize
- **Lambda layers** — store Python source code, hard to parse structurally
- **Subclassed models** — `get_config()` may not work; only Sequential/Functional have full configs

---

## 9. ONNX Layer Type Representation

### 9.1 ONNX Operator Set

ONNX represents layers as **operators** in its graph. The operator set is versioned (currently opset 21). Key operator categories:

#### Convolution Operators

| ONNX Op | Description | Key Attributes |
|---|---|---|
| `Conv` | N-D convolution | `kernel_shape`, `strides`, `pads`, `group`, `dilations`, `auto_pad` |
| `ConvTranspose` | Transposed (deconvolution) | `kernel_shape`, `strides`, `output_padding`, `group` |
| `DepthToSpace` | Rearrange depth data into spatial | `blocksize`, `mode` (CRS, DCR) |
| `SpaceToDepth` | Rearrange spatial data into depth | `blocksize` |

**Conv node in protobuf:**
```
NodeProto {
  op_type: "Conv"
  input: ["input", "weight", "bias"]    // bias optional
  output: ["output"]
  attribute: [
    {name: "kernel_shape", type: INTS, ints: [3, 3]},
    {name: "strides", type: INTS, ints: [1, 1]},
    {name: "pads", type: INTS, ints: [1, 1, 1, 1]},
    {name: "dilations", type: INTS, ints: [1, 1]},
    {name: "group", type: INT, i: 1}
  ]
}
```

#### Pooling Operators

| ONNX Op | Description | Key Attributes |
|---|---|---|
| `MaxPool` | Max pooling | `kernel_shape`, `strides`, `pads`, `ceil_mode` |
| `AveragePool` | Average pooling | Same + `count_include_pad` |
| `GlobalAveragePool` | Global average pooling | None |
| `GlobalMaxPool` | Global max pooling | None |
| `AdaptiveAvgPool` | Adaptive average pooling | `output_size` |

#### Activation Functions

| ONNX Op | Notes |
|---|---|
| `Relu` | No attributes |
| `Sigmoid` | No attributes |
| `Tanh` | No attributes |
| `LeakyRelu` | `alpha` attribute |
| `Elu` | `alpha` attribute |
| `Selu` | `alpha`, `gamma` |
| `Softmax` | `axis` attribute |
| `Gelu` | Opset 20+ |
| `Silu` | Opset 22+ (Swish) |
| `PRelu` | Slope as input tensor |

#### Normalization

| ONNX Op | Key Attributes |
|---|---|
| `BatchNormalization` | `epsilon`, `momentum`, `training_mode` |
| `InstanceNormalization` | `epsilon` |
| `LayerNormalization` | `axis`, `epsilon`, `stash_type` |
| `GroupNormalization` | `num_groups`, `epsilon` |

#### Recurrent / Sequence

| ONNX Op | Key Attributes |
|---|---|
| `LSTM` | `hidden_size`, `direction` (forward/reverse/bidirectional), `activation_alpha`, `activation_beta`, `activations`, `clip`, `input_forget` |
| `GRU` | `hidden_size`, `direction`, `linear_before_reset` |
| `RNN` | `hidden_size`, `direction` |
| `SequenceConstruct` | Variable-length sequences |
| `SequenceAt` | Index into sequence |

**LSTM in protobuf:**
```
NodeProto {
  op_type: "LSTM"
  input: ["X", "W", "R", "B", "sequence_lens", "initial_h", "initial_c"]
  output: ["Y", "Y_h", "Y_c"]
  attribute: [
    {name: "hidden_size", type: INT, i: 256},
    {name: "direction", type: STRING, s: "bidirectional"},
    {name: "activations", type: STRINGS, strings: ["Sigmoid", "Tanh", "Tanh"]}
  ]
}
```

#### Attention / Transformer

| ONNX Op | Description | Key Attributes |
|---|---|---|
| `Attention` | Fused attention (opset 23+) | `num_heads`, `qkv_hidden_sizes`, `is_unidirectional`, `scale`, `softmax_precision` |
| `MultiHeadAttention` | MHA (opset 22+) | `num_heads`, `k_num_heads`, `qkv_hidden_sizes` |
| `RotaryEmbedding` | RoPE (opset 23+) | `interleaved`, `num_heads` |
| `SkipLayerNormalization` | Fused skip+layernorm | Custom op (contrib) |

#### Tensor Operations

| ONNX Op | Description |
|---|---|
| `MatMul` | Matrix multiplication |
| `Gemm` | General matrix multiply (`alpha`, `beta`, `transA`, `transB`) |
| `Reshape` | Shape transformation |
| `Transpose` | Permute axes (`perm`) |
| `Concat` | Concatenate along axis |
| `Slice` | Slice tensor |
| `Squeeze` / `Unsqueeze` | Remove/add dimensions |
| `Gather` | Index into tensor |
| `ScatterND` | Scatter updates |

#### Element-wise

| ONNX Op | Description |
|---|---|
| `Add`, `Sub`, `Mul`, `Div` | Arithmetic |
| `Pow` | Power |
| `Exp`, `Log`, `Sqrt` | Math |
| `ReduceMean`, `ReduceSum`, `ReduceMax` | Reductions |
| `Clip` | Clamp values (`min`, `max`) |
| `Where` | Conditional selection |
| `Equal`, `Greater`, `Less` | Comparison |

### 9.2 Layer Categorization for Visualization

```python
OP_CATEGORIES = {
    # Convolution
    "Conv": "convolution", "ConvTranspose": "convolution",
    # Pooling
    "MaxPool": "pooling", "AveragePool": "pooling",
    "GlobalMaxPool": "pooling", "GlobalAveragePool": "pooling",
    "AdaptiveAvgPool": "pooling", "AdaptiveMaxPool": "pooling",
    # Activations
    "Relu": "activation", "Sigmoid": "activation", "Tanh": "activation",
    "LeakyRelu": "activation", "Elu": "activation", "Selu": "activation",
    "Softmax": "activation", "Gelu": "activation", "Silu": "activation",
    "PRelu": "activation", "HardSigmoid": "activation", "HardSwish": "activation",
    # Normalization
    "BatchNormalization": "normalization", "InstanceNormalization": "normalization",
    "LayerNormalization": "normalization", "GroupNormalization": "normalization",
    # Linear / Matrix
    "Gemm": "linear", "MatMul": "linear",
    # Recurrent
    "LSTM": "recurrent", "GRU": "recurrent", "RNN": "recurrent",
    # Attention
    "Attention": "attention", "MultiHeadAttention": "attention",
    # Reshape / Movement
    "Reshape": "reshape", "Transpose": "reshape", "Squeeze": "reshape",
    "Unsqueeze": "reshape", "Flatten": "reshape", "Expand": "reshape",
    # Merge / Split
    "Concat": "merge", "Add": "elementwise", "Mul": "elementwise",
    "Sub": "elementwise", "Div": "elementwise",
    # Data
    "Gather": "data", "Slice": "data", "Pad": "data",
    # Reduction
    "ReduceMean": "reduction", "ReduceSum": "reduction",
    # Control
    "If": "control", "Loop": "control", "Scan": "control",
}
```

---

## 10. FLOPs Calculation from ONNX

### 10.1 Methodology

FLOPs (Floating Point Operations) must be calculated per-operator type:

| Operator | FLOPs Formula |
|---|---|
| **Conv** | `2 × out_channels × in_channels/groups × kH × kW × outH × outW × batch` |
| **MatMul / Gemm** | `2 × M × K × N` (where M,K,N are matrix dimensions) |
| **BatchNorm** | `2 × elements` (multiply + add per element) |
| **ReLU** | `elements` (1 comparison per element) |
| **Pooling** | `kernel_H × kernel_W × outH × outW × channels` |

### 10.2 Implementation

```python
import onnx
from onnx import numpy_helper, shape_inference, TensorProto
import numpy as np

def calculate_flops(model_path: str) -> dict:
    """Calculate FLOPs for an ONNX model."""
    model = onnx.load(model_path)
    model = shape_inference.infer_shapes(model)
    graph = model.graph
    
    # Build shape map from inputs and initializers
    shape_map = {}
    for inp in graph.input:
        shape = []
        for dim in inp.type.tensor_type.shape.dim:
            shape.append(dim.dim_value if dim.dim_value else 1)
        shape_map[inp.name] = shape
    
    for init in graph.initializer:
        shape_map[init.name] = list(init.dims)
    
    total_flops = 0
    layer_flops = {}
    
    for node in graph.node:
        flops = 0
        
        if node.op_type == "Conv":
            # Get kernel shape from attributes or weight tensor
            kernel_shape = None
            for attr in node.attribute:
                if attr.name == "kernel_shape":
                    kernel_shape = list(attr.ints)
            
            if not kernel_shape and len(node.input) > 1:
                weight_shape = shape_map.get(node.input[1], [])
                if len(weight_shape) >= 3:
                    kernel_shape = weight_shape[2:]
            
            # Get group count
            group = 1
            for attr in node.attribute:
                if attr.name == "group":
                    group = attr.i
            
            if kernel_shape and len(node.input) > 1:
                weight_shape = shape_map.get(node.input[1], [])
                out_channels = weight_shape[0] if weight_shape else 1
                in_channels = weight_shape[1] if len(weight_shape) > 1 else 1
                
                # Output spatial dims (approximate)
                out_shape = shape_map.get(node.output[0], [])
                out_elements = np.prod(out_shape) if out_shape else 1
                
                flops = 2 * out_channels * (in_channels // group) * np.prod(kernel_shape) * (out_elements / out_channels)
        
        elif node.op_type in ("MatMul", "Gemm"):
            a_shape = shape_map.get(node.input[0], [])
            b_shape = shape_map.get(node.input[1], [])
            
            if node.op_type == "Gemm":
                transA, transB = 0, 0
                for attr in node.attribute:
                    if attr.name == "transA": transA = attr.i
                    if attr.name == "transB": transB = attr.i
                
                M = a_shape[-(1 if transA else 0)] if a_shape else 1
                K = a_shape[-(0 if transA else 1)] if a_shape else 1
                N = b_shape[-(0 if transB else 1)] if b_shape else 1
                flops = 2 * M * K * N
            elif a_shape and b_shape:
                # MatMul: last two dims
                M, K = a_shape[-2], a_shape[-1]
                N = b_shape[-1]
                flops = 2 * M * K * N
                # Multiply by batch dimensions
                batch = np.prod(a_shape[:-2]) if len(a_shape) > 2 else 1
                flops *= batch
        
        elif node.op_type == "BatchNormalization":
            out_shape = shape_map.get(node.output[0], [])
            flops = 2 * np.prod(out_shape) if out_shape else 0
        
        elif node.op_type in ("Relu", "Sigmoid", "Tanh", "LeakyRelu", "Elu", "Selu"):
            out_shape = shape_map.get(node.output[0], [])
            flops = np.prod(out_shape) if out_shape else 0
        
        elif node.op_type in ("MaxPool", "AveragePool"):
            kernel_shape = None
            for attr in node.attribute:
                if attr.name == "kernel_shape":
                    kernel_shape = list(attr.ints)
            out_shape = shape_map.get(node.output[0], [])
            if kernel_shape and out_shape:
                flops = np.prod(kernel_shape) * np.prod(out_shape)
        
        elif node.op_type == "LSTM":
            hidden_size = 0
            for attr in node.attribute:
                if attr.name == "hidden_size":
                    hidden_size = attr.i
            input_shape = shape_map.get(node.input[0], [])
            seq_len = input_shape[1] if len(input_shape) > 1 else 1
            batch = input_shape[0] if input_shape else 1
            # LSTM: 4 gates × (input_size + hidden_size) × hidden_size per timestep
            input_size = input_shape[2] if len(input_shape) > 2 else 1
            direction = "forward"
            for attr in node.attribute:
                if attr.name == "direction":
                    direction = attr.s.decode()
            dir_mult = 2 if direction == "bidirectional" else 1
            flops = seq_len * batch * dir_mult * 4 * (input_size + hidden_size) * hidden_size
        
        elif node.op_type in ("Relu", "Softmax"):
            out_shape = shape_map.get(node.output[0], [])
            flops = int(np.prod(out_shape)) if out_shape else 0
        
        # Update shape map with output shapes
        if node.output:
            out_info = None
            for vi in graph.value_info:
                if vi.name == node.output[0]:
                    out_info = vi
                    break
            if out_info and out_info.type.tensor_type.shape:
                shape_map[node.output[0]] = [
                    d.dim_value if d.dim_value else 1
                    for d in out_info.type.tensor_type.shape.dim
                ]
        
        layer_flops[node.name or f"{node.op_type}_{id(node)}"] = flops
        total_flops += flops
    
    return {
        "total_flops": total_flops,
        "total_gflops": total_flops / 1e9,
        "per_layer": layer_flops,
    }
```

### 10.3 Using onnx-tool (Recommended)

```python
import onnx_tool

# Simple profiling
model = onnx_tool.Model("model.onnx")
model.shape_infer()  # run shape inference first
model.profile()      # prints MACs per layer

# Programmatic access
# onnx_tool provides per-node MACs and parameter counts
```

### 10.4 Important Notes

- **MACs vs FLOPs** — many tools report MACs (multiply-accumulate). `FLOPs ≈ 2 × MACs`
- **Shape inference required** — output shapes must be known for FLOPs calculation
- **Dynamic shapes** — use default batch=1 for profiling
- **Sparsity** — real FLOPs may be lower with sparse models (onnx-tool handles this)

---

## 11. Memory Footprint Estimation

### 11.1 Components of Model Memory

| Component | What It Is | How to Calculate |
|---|---|---|
| **Weights (parameters)** | Model weights in memory | `sum(param_size × bytes_per_element)` |
| **Activations** | Intermediate tensors during inference | `sum(output_tensor_size × bytes_per_element)` |
| **KV Cache** | For autoregressive models | `2 × num_layers × hidden_dim × seq_len × bytes` |
| **Gradients** | Only during training | Same as weights |
| **Optimizer states** | Only during training | 2× weights for Adam |

### 11.2 Implementation

```python
import onnx
from onnx import numpy_helper, TensorProto
import numpy as np

DTYPE_SIZES = {
    TensorProto.FLOAT: 4,     # FP32
    TensorProto.FLOAT16: 2,   # FP16
    TensorProto.BFLOAT16: 2,  # BF16
    TensorProto.DOUBLE: 8,    # FP64
    TensorProto.INT8: 1,      # INT8
    TensorProto.UINT8: 1,
    TensorProto.INT16: 2,
    TensorProto.INT32: 4,
    TensorProto.INT64: 8,
    TensorProto.UINT4: 0.5,   # Packed
    TensorProto.INT4: 0.5,
    TensorProto.BOOL: 1,
}

def estimate_memory(model_path: str) -> dict:
    """Estimate memory footprint of an ONNX model."""
    model = onnx.load(model_path)
    model = shape_inference.infer_shapes(model)
    graph = model.graph
    
    # 1. Weight memory
    weight_bytes_fp32 = 0
    weight_bytes_native = 0
    weight_count = 0
    
    for init in graph.initializer:
        elem_size = DTYPE_SIZES.get(init.data_type, 4)
        n_elements = np.prod(init.dims) if init.dims else 1
        weight_bytes_native += int(n_elements * elem_size)
        weight_bytes_fp32 += int(n_elements * 4)  # FP32 equivalent
        weight_count += n_elements
    
    # 2. Activation memory (from shape-inferred outputs)
    activation_bytes = 0
    activation_details = []
    
    for vi in graph.value_info:
        if vi.type.tensor_type.HasField("shape"):
            shape = [d.dim_value for d in vi.type.tensor_type.shape.dim if d.dim_value]
            elem_size = DTYPE_SIZES.get(vi.type.tensor_type.elem_type, 4)
            tensor_bytes = int(np.prod(shape)) * elem_size if shape else 0
            activation_bytes += tensor_bytes
            activation_details.append({
                "name": vi.name,
                "shape": shape,
                "bytes": tensor_bytes,
            })
    
    # 3. Peak memory estimation
    # Peak is roughly: weights + max_concurrent_activations
    # For simple estimate: weights + sum_of_all_activations (upper bound)
    peak_memory = weight_bytes_native + activation_bytes
    
    return {
        "weights_fp32_bytes": weight_bytes_fp32,
        "weights_fp32_mb": weight_bytes_fp32 / (1024**2),
        "weights_native_bytes": weight_bytes_native,
        "weights_native_mb": weight_bytes_native / (1024**2),
        "total_params": weight_count,
        "activations_bytes": activation_bytes,
        "activations_mb": activation_bytes / (1024**2),
        "peak_memory_bytes": peak_memory,
        "peak_memory_mb": peak_memory / (1024**2),
        "activation_details": sorted(activation_details, key=lambda x: -x["bytes"])[:20],
    }
```

### 11.3 Quantization Impact

| Precision | Bytes/Element | Relative Size | Typical Use |
|---|---|---|---|
| FP32 | 4 | 1.0× | Training, reference |
| FP16/BF16 | 2 | 0.5× | Mixed precision, inference |
| INT8 | 1 | 0.25× | Quantized inference |
| INT4 | 0.5 | 0.125× | LLM quantization (GPTQ, AWQ) |
| NF4 | 0.5 | 0.125× | QLoRA |

---

## 12. Architecture Anti-pattern Detection

### 12.1 Common Anti-patterns

| Anti-pattern | Detection Method | Severity | Suggestion |
|---|---|---|---|
| **Redundant Reshape** | Consecutive Reshape→Reshape with same shape | Warning | Remove intermediate Reshape |
| **Unnecessary Cast** | Cast→Cast chain (e.g., FP32→FP16→FP32) | Warning | Remove identity casts |
| **Redundant Transpose** | Transpose→Transpose where perm composition = identity | Warning | Fuse into single Transpose or remove |
| **Unused outputs** | Graph outputs that are never consumed | Info | Remove unused outputs |
| **Large kernel without pooling** | Conv with kernel > 7×7 and no following pool | Info | Consider smaller kernel + pooling |
| **Missing batch norm after conv** | Conv followed directly by activation without BN/LN | Info | Consider adding normalization |
| **Too many consecutive FC layers** | >3 Gemm/MatMul in sequence | Warning | Consider residual connections |
| **Vanishing gradient risk** | Deep network (>20 layers) without skip connections | Warning | Add residual/skip connections |
| **Expensive attention on large tensors** | Attention with sequence length > 4096 | Warning | Use efficient attention variants |
| **Redundant Softmax** | Softmax→Softmax | Error | Remove duplicate |
| **Reshape before output** | Reshape as last op (often unnecessary) | Info | May indicate framework artifact |
| **Identity operations** | Ops that don't change data (Add with 0, Mul with 1) | Warning | Remove identity ops |
| **Inefficient Conv groups** | Conv with groups=1 where depthwise could be used | Info | Consider depthwise separable |
| **Missing bias in last layer** | Final Gemm/Conv without bias | Info | Verify intentional |

### 12.2 Implementation

```python
import onnx
from onnx import shape_inference

def detect_anti_patterns(model_path: str) -> list[dict]:
    """Detect common architecture anti-patterns."""
    model = onnx.load(model_path)
    model = shape_inference.infer_shapes(model)
    graph = model.graph
    
    issues = []
    nodes = list(graph.node)
    
    # Build adjacency: output_name → consuming node(s)
    output_to_consumers = {}
    for node in nodes:
        for inp in node.input:
            output_to_consumers.setdefault(inp, []).append(node)
    
    for i, node in enumerate(nodes):
        
        # 1. Redundant Reshape
        if node.op_type == "Reshape":
            if i + 1 < len(nodes) and nodes[i+1].op_type == "Reshape":
                issues.append({
                    "type": "redundant_reshape",
                    "severity": "warning",
                    "location": node.name or f"node_{i}",
                    "description": "Two consecutive Reshape operations",
                    "suggestion": "Merge into a single Reshape or remove intermediate",
                })
        
        # 2. Unnecessary Cast chains
        if node.op_type == "Cast":
            if i + 1 < len(nodes) and nodes[i+1].op_type == "Cast":
                issues.append({
                    "type": "redundant_cast",
                    "severity": "warning",
                    "location": node.name or f"node_{i}",
                    "description": "Two consecutive Cast operations",
                    "suggestion": "Remove identity casts or fuse into single Cast",
                })
        
        # 3. Redundant Transpose
        if node.op_type == "Transpose":
            if i + 1 < len(nodes) and nodes[i+1].op_type == "Transpose":
                perm1 = [a for a in node.attribute if a.name == "perm"]
                perm2 = [a for a in nodes[i+1].attribute if a.name == "perm"]
                if perm1 and perm2:
                    p1, p2 = list(perm1[0].ints), list(perm2[0].ints)
                    composed = [p1[p2[j]] for j in range(len(p1))]
                    if composed == list(range(len(p1))):
                        issues.append({
                            "type": "redundant_transpose",
                            "severity": "warning",
                            "location": node.name or f"node_{i}",
                            "description": "Two Transpose ops that compose to identity",
                            "suggestion": "Remove both Transpose operations",
                        })
        
        # 4. Redundant Softmax
        if node.op_type == "Softmax":
            consumers = output_to_consumers.get(node.output[0], [])
            for c in consumers:
                if c.op_type == "Softmax":
                    issues.append({
                        "type": "redundant_softmax",
                        "severity": "error",
                        "location": node.name or f"node_{i}",
                        "description": "Softmax followed by another Softmax",
                        "suggestion": "Remove the duplicate Softmax",
                    })
        
        # 5. Identity operations
        if node.op_type == "Add":
            for inp_name in node.input:
                for init in graph.initializer:
                    if init.name == inp_name:
                        w = numpy_helper.to_array(init)
                        if np.all(w == 0):
                            issues.append({
                                "type": "identity_add",
                                "severity": "warning",
                                "location": node.name or f"node_{i}",
                                "description": "Add with zero tensor (identity operation)",
                                "suggestion": "Remove the Add node",
                            })
        
        if node.op_type == "Mul":
            for inp_name in node.input:
                for init in graph.initializer:
                    if init.name == inp_name:
                        w = numpy_helper.to_array(init)
                        if np.all(w == 1):
                            issues.append({
                                "type": "identity_mul",
                                "severity": "warning",
                                "location": node.name or f"node_{i}",
                                "description": "Mul with ones tensor (identity operation)",
                                "suggestion": "Remove the Mul node",
                            })
    
    # 6. Deep network without skip connections
    conv_count = sum(1 for n in nodes if n.op_type in ("Conv", "ConvTranspose"))
    add_count = sum(1 for n in nodes if n.op_type == "Add")
    if conv_count > 20 and add_count < conv_count * 0.1:
        issues.append({
            "type": "deep_no_skip",
            "severity": "warning",
            "location": "global",
            "description": f"Deep network ({conv_count} conv layers) with few skip connections ({add_count} Add ops)",
            "suggestion": "Consider adding residual connections to prevent vanishing gradients",
        })
    
    # 7. Large attention without efficient variant
    for node in nodes:
        if node.op_type in ("Attention", "MultiHeadAttention"):
            # Check if input has large sequence dimension
            for vi in graph.value_info:
                if vi.name == node.input[0] and vi.type.tensor_type.HasField("shape"):
                    dims = [d.dim_value for d in vi.type.tensor_type.shape.dim if d.dim_value]
                    if len(dims) >= 3 and dims[1] > 4096:  # seq_len > 4096
                        issues.append({
                            "type": "large_attention",
                            "severity": "warning",
                            "location": node.name or f"node_{i}",
                            "description": f"Attention on sequence length {dims[1]}",
                            "suggestion": "Consider Flash Attention or sparse attention variants",
                        })
    
    return issues
```

---

## 13. Recommended Architecture & Integration

### 13.1 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React)                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  File Upload│  │  3D Canvas   │  │  Details Panel   │ │
│  │  Component  │  │  (R3F/Drei)  │  │  (Layer Info)    │ │
│  └──────┬─────┘  └──────┬───────┘  └────────┬─────────┘ │
│         │               │                    │           │
│  ┌──────┴───────────────┴────────────────────┴─────────┐ │
│  │              State Management (Zustand/Jotai)        │ │
│  └──────────────────────┬──────────────────────────────┘ │
└─────────────────────────┼────────────────────────────────┘
                          │ REST API / WebSocket
┌─────────────────────────┼────────────────────────────────┐
│                   Backend (FastAPI)                       │
│  ┌──────────────────────┴──────────────────────────────┐ │
│  │                  API Router                          │ │
│  └──┬──────────┬──────────────┬────────────────────────┘ │
│     │          │              │                           │
│  ┌──┴───┐  ┌──┴────┐  ┌─────┴──────┐  ┌──────────────┐ │
│  │ ONNX │  │PyTorch│  │   Keras    │  │  Analysis     │ │
│  │Parser│  │Parser │  │  Parser    │  │  Engine       │ │
│  └──┬───┘  └──┬────┘  └─────┬──────┘  │ • FLOPs      │ │
│     │         │             │          │ • Memory      │ │
│     └─────────┴──────┬──────┘          │ • Anti-pattern│ │
│                      │                 └──────────────┘ │
│              ┌───────┴─────────┐                         │
│              │  Unified Graph  │                         │
│              │  Representation │                         │
│              └─────────────────┘                         │
└──────────────────────────────────────────────────────────┘
```

### 13.2 Unified Internal Graph Format

```python
from pydantic import BaseModel
from typing import Optional

class TensorShape(BaseModel):
    dims: list[int | str]  # int for concrete, str for symbolic
    dtype: str

class NodeInfo(BaseModel):
    id: str                    # unique node ID
    name: str                  # human-readable name
    op_type: str               # e.g., "Conv", "Relu"
    category: str              # "convolution", "activation", etc.
    inputs: list[str]          # input tensor names
    outputs: list[str]         # output tensor names
    input_shapes: list[TensorShape]
    output_shapes: list[TensorShape]
    attributes: dict           # op-specific attributes
    param_count: int
    flops: int

class EdgeInfo(BaseModel):
    source_node: str
    source_output: str
    target_node: str
    target_input: str
    tensor_shape: Optional[TensorShape]

class ModelGraph(BaseModel):
    name: str
    format: str                # "onnx", "pytorch", "keras"
    nodes: list[NodeInfo]
    edges: list[EdgeInfo]
    inputs: list[NodeInfo]     # graph input nodes
    outputs: list[NodeInfo]    # graph output nodes
    total_params: int
    total_flops: int
    metadata: dict
```

### 13.3 Tech Stack Summary

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend Framework** | React 18 | 18.3+ | UI framework |
| **3D Rendering** | Three.js + @react-three/fiber | r175+ / v9+ | 3D neural network visualization |
| **3D Helpers** | @react-three/drei | v10+ | Controls, HTML overlays, text |
| **State** | Zustand or Jotai | Latest | Lightweight state management |
| **Styling** | Tailwind CSS + Radix UI | Latest | UI components and styling |
| **Backend** | FastAPI | 0.138+ | Python API server |
| **ONNX Parsing** | onnx + onnx-tool | 1.17+ / 1.0+ | Model parsing and profiling |
| **PyTorch Support** | torch + torchinfo | 2.x | .pt file loading and analysis |
| **Keras Support** | keras + h5py | 3.x | .h5/.keras parsing |
| **Visualization Export** | Three.js GLTFExporter | Built-in | GLB/GLTF export |
| **Charts** | Recharts or Nivo | Latest | FLOPs/params bar charts |

### 13.4 Key Design Decisions

1. **Backend-heavy parsing** — ONNX/PyTorch/Keras parsing happens server-side; frontend receives clean JSON graph
2. **ONNX as lingua franca** — convert PyTorch/Keras to ONNX for unified analysis
3. **react-three-fiber** — React-native 3D rendering with JSX; better DX than raw Three.js
4. **Per-layer visual encoding** — shape = op category, color = layer type, size = param count
5. **Progressive loading** — use WebSocket for real-time progress on large model uploads
6. **Export formats** — GLB for 3D scenes, JSON for graph data, CSV for profiling reports

### 13.5 Implementation Roadmap

| Phase | Deliverable | Duration |
|---|---|---|
| **Phase 1** | Backend: ONNX parser + API + FLOPs/memory analysis | 2 weeks |
| **Phase 2** | Frontend: 3D canvas + layer rendering + click interaction | 2 weeks |
| **Phase 3** | Integration: file upload → parse → visualize pipeline | 1 week |
| **Phase 4** | Multi-format: PyTorch + Keras support | 1 week |
| **Phase 5** | Analysis: anti-pattern detection + profiling dashboard | 1 week |
| **Phase 6** | Polish: export, responsive UI, performance optimization | 1 week |

---

## Appendix A: Quick Reference — npm/pip Packages

### Python (Backend)

```
fastapi==0.138.0
uvicorn[standard]
python-multipart
onnx>=1.17.0
onnx-tool>=1.0.0
onnxruntime>=1.21.0
numpy
torch>=2.0.0  # for .pt support
keras>=3.0.0  # for .keras support
h5py  # for .h5 support
```

### JavaScript (Frontend)

```
react>=18.3.0
three>=0.175.0
@react-three/fiber>=9.0.0
@react-three/drei>=10.0.0
zustand  # state management
tailwindcss  # styling
```

## Appendix B: Operator Count by Category (ONNX opset 21)

| Category | Operator Count | Examples |
|---|---|---|
| Arithmetic | ~15 | Add, Sub, Mul, Div, Pow, Mod |
| Activation | ~12 | Relu, Sigmoid, Tanh, Gelu, Silu |
| Convolution | 3 | Conv, ConvTranspose, QLinearConv |
| Pooling | 7 | MaxPool, AveragePool, GlobalAvg, LpPool |
| Normalization | 5 | BatchNorm, LayerNorm, GroupNorm, InstanceNorm |
| Reduction | 9 | ReduceMean, ReduceSum, ReduceMax, ArgMax |
| Tensor | ~25 | Reshape, Transpose, Concat, Split, Gather |
| Recurrent | 3 | LSTM, GRU, RNN |
| Attention | 3 | Attention, MultiHeadAttention, RotaryEmbedding |
| Quantization | ~8 | QuantizeLinear, DequantizeLinear, QLinearMatMul |
| Logical/Comparison | ~10 | Equal, Greater, Less, And, Or, Not |
| Other | ~50+ | Cast, Shape, Size, Constant, If, Loop, Scan |

**Total: 170+ operators in ONNX opset 21**

---

*Report generated 2026-06-25. All versions and data current as of research date.*
