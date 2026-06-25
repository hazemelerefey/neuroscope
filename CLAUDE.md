# CLAUDE.md — NeuroScope Project Context

> **This file is for AI coding agents (Claude Code, Cursor, Copilot, etc.)**
> It contains everything you need to understand the project and help build it.

---

## 🧠 What Is NeuroScope?

NeuroScope is a **web-based tool** that lets ML students and developers:

1. **Upload** a neural network model file (`.onnx`, `.pt`, `.h5`, `.tflite`)
2. **Visualize** the architecture in interactive 3D (Three.js)
3. **Analyze** the design with an automated "ML linter" that detects anti-patterns
4. **Export** 3D models, diagrams, and analysis reports

**Tagline:** "modelviz shows you what your model looks like. NeuroScope tells you what's wrong with it."

**Target competition:** Presidential African Youth in AI and Robotics Competition 2026 (AYAIR) — Education Enhancement category.

**GitHub:** https://github.com/hazemelerefey/neuroscope

---

## 🏗️ Architecture Overview

```
User uploads .onnx file
        │
        ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   PARSER    │────▶│ GRAPH BUILDER│────▶│   ANALYZER    │
│  (ONNX/     │     │  (Nodes +    │     │  (Rules       │
│   PyTorch/  │     │   Edges)     │     │   Engine)     │
│   Keras)    │     └──────────────┘     └───────┬───────┘
└─────────────┘                                  │
        ┌────────────────────────────────────────┼──────────┐
        ▼                                        ▼          ▼
 ┌──────────┐                          ┌──────────┐  ┌──────────┐
 │  3D View │                          │ Analysis │  │  Export  │
 │ (Three.js│                          │ Panel    │  │ GLB/SVG/ │
 │  React)  │                          │          │  │ PDF/MD   │
 └──────────┘                          └──────────┘  └──────────┘
```

### Data Flow

1. **Upload** → User drags `.onnx` file → FastAPI receives it → ONNX parser extracts graph
2. **Graph** → Unified `NeuroScopeGraph` data structure (nodes + edges + stats)
3. **Analysis** → Rules engine checks graph → produces `AnalysisReport` (findings + health score)
4. **Visualization** → Graph data sent to frontend → Three.js renders 3D model
5. **Export** → Generate GLB/SVG/PDF/MD from graph + analysis results

---

## 📁 Project Structure

```
neuroscope/
├── src/                              # Python backend (FastAPI)
│   ├── main.py                       # FastAPI app entry point
│   ├── __init__.py
│   │
│   ├── parsers/                      # Model file parsers
│   │   ├── __init__.py               # BaseParser abstract class
│   │   ├── onnx_parser.py            # ✅ COMPLETE — ONNX protobuf parser
│   │   ├── pytorch_parser.py         # ❌ MISSING — .pt/.pth files
│   │   ├── keras_parser.py           # ❌ MISSING — .h5/.keras files
│   │   └── tflite_parser.py          # ❌ MISSING — .tflite files
│   │
│   ├── graph/                        # Internal graph representation
│   │   └── __init__.py               # ✅ LayerNode, Edge, Finding, AnalysisReport, NeuroScopeGraph
│   │   # ❌ MISSING: builder.py, skip_detector.py, group.py, classifier.py
│   │
│   ├── analysis/                     # Architecture analysis engine
│   │   ├── __init__.py               # ✅ AnalysisEngine orchestrator
│   │   ├── flops.py                  # ⚠️ HAS BUGS — FLOPs calculator
│   │   ├── memory.py                 # ✅ Memory + training time estimator
│   │   ├── rules/
│   │   │   ├── __init__.py
│   │   │   ├── layer_rules.py        # ✅ 4 layer-level rules
│   │   │   ├── architecture_rules.py # ✅ 4 architecture rules
│   │   │   ├── efficiency_rules.py   # ⚠️ HAS BUGS — stride detection
│   │   │   └── task_rules.py         # ❌ MISSING — 18 task-specific rules
│   │   └── model_card.py             # ❌ MISSING — auto model card generator
│   │
│   ├── api/                          # FastAPI routes
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py             # ⚠️ HAS BUGS — doesn't store graph
│   │   │   ├── analyze.py            # ⚠️ HAS BUGS — graph_store empty
│   │   │   ├── export.py             # ⚠️ STUB — only placeholder
│   │   │   └── compare.py            # ⚠️ STUB — not implemented
│   │   └── store.py                  # ❌ MISSING — shared graph store
│   │
│   ├── export/                       # Export engines
│   │   ├── glb_exporter.py           # ❌ MISSING — 3D model export
│   │   ├── svg_exporter.py           # ❌ MISSING — 2D diagram export
│   │   ├── pdf_exporter.py           # ❌ MISSING — report export
│   │   └── markdown_exporter.py      # ❌ MISSING — markdown export
│   │
│   └── utils/                        # ❌ EMPTY — shared utilities
│
├── frontend/                         # React + Three.js web app
│   ├── index.html                    # Entry HTML
│   ├── package.json                  # Dependencies
│   ├── vite.config.ts                # Vite config with API proxy
│   ├── tsconfig.json                 # ⚠️ References missing tsconfig.node.json
│   │
│   └── src/
│       ├── main.tsx                  # React entry point
│       ├── App.tsx                   # ⚠️ HAS BUGS — data shape mismatch
│       ├── index.css                 # ✅ Full dark theme styling
│       │
│       ├── components/
│       │   ├── UploadZone.tsx        # ✅ Drag & drop file upload
│       │   ├── Canvas3D.tsx          # ⚠️ HAS BUGS — reads wrong data shape
│       │   ├── AnalysisPanel.tsx     # ⚠️ Needs wiring to backend
│       │   ├── StatsPanel.tsx        # ⚠️ HAS BUGS — reads wrong data shape
│       │   └── ExportMenu.tsx        # ⚠️ Only 2/5 formats work
│       │
│       ├── hooks/                    # ❌ EMPTY — custom React hooks
│       ├── three/                    # ❌ EMPTY — Three.js utilities
│       └── utils/                    # ❌ EMPTY — frontend utilities
│
├── config/                           # Configuration files
│   ├── analysis_rules.yaml           # ✅ Rule thresholds + hardware presets
│   ├── layer_shapes.yaml             # ✅ Layer → 3D shape mapping
│   └── languages/
│       ├── en.json                   # ⚠️ BROKEN — YAML syntax in .json file
│       ├── fr.json                   # ❌ MISSING
│       ├── ar.json                   # ❌ MISSING
│       ├── sw.json                   # ❌ MISSING
│       └── pt.json                   # ❌ MISSING
│
├── tests/                            # Test suite
│   ├── test_parsers/
│   │   └── test_onnx_parser.py       # ⚠️ Missing BaseParser import
│   ├── test_analysis/
│   │   ├── test_rules.py             # ✅ 12 test cases
│   │   └── test_flops.py             # ⚠️ MatMul test passes by coincidence
│   └── test_graph/
│       └── test_graph.py             # ✅ 4 test cases
│
├── data/                             # Sample models
│   ├── samples/                      # ❌ EMPTY — needs .onnx sample files
│   └── fixtures/                     # ❌ EMPTY — test data
│
├── docker/                           # Containerization
│   ├── Dockerfile.backend            # ✅ Python backend
│   └── Dockerfile.frontend           # ✅ Node frontend
│
├── docker-compose.yml                # ✅ Full stack deployment
├── requirements.txt                  # ✅ Python dependencies
├── LICENSE                           # ✅ MIT License
├── .gitignore                        # ✅ Python + Node + Docker
├── README.md                         # ✅ Full project README
│
├── competition/                      # Competition submission materials
│   ├── registration.md               # ✅ Form fields + team info template
│   ├── timeline.md                   # ✅ All competition dates
│   └── essay_draft.md                # ⚠️ OUTLINE ONLY — needs 800-word essay
│
├── research/                         # Deep research reports (198KB)
│   ├── tech_stack.md                 # ✅ 71KB — ONNX, Three.js, FastAPI research
│   ├── ml_anti_patterns.md           # ✅ 48KB — 47 anti-patterns catalog
│   ├── african_ml_landscape.md       # ✅ 32KB — Africa ML ecosystem
│   ├── competitor_analysis.md        # ✅ 26KB — 15 tools analyzed
│   └── competition_details.md        # ✅ 21KB — AYAIR rules & judging
│
└── docs/                             # Documentation
    ├── architecture_brainstorm.md    # ✅ 22KB — full architecture design
    ├── code_review.md                # ✅ Python code review (20 issues)
    ├── frontend_review.md            # ✅ Frontend review (16 issues)
    └── project_review.md             # ✅ Project review (30+ issues)
```

---

## 🔴 Known Critical Bugs (Must Fix)

### BUG-01: `graph_store` not shared between API routes

**Files:** `src/api/routes/upload.py` + `src/api/routes/analyze.py`

**Problem:** `upload.py` parses the model but never stores the graph. `analyze.py` has its own empty `graph_store`. The `/analyze` endpoint always returns 404.

**Fix:** Create `src/api/store.py` with a shared dict. Import it in both routes.

```python
# src/api/store.py
from src.graph import NeuroScopeGraph
graph_store: dict[str, NeuroScopeGraph] = {}
```

Then in `upload.py`:
```python
from src.api.store import graph_store
# After parsing: graph_store[model_id] = graph
```

And in `analyze.py`:
```python
from src.api.store import graph_store
# Remove the local graph_store definition
```

---

### BUG-02: Frontend data shape mismatch

**Files:** `App.tsx`, `Canvas3D.tsx`, `StatsPanel.tsx`

**Problem:** Backend returns `{ graph_json: { nodes: [...], edges: [...] }, model_name: ... }`. Frontend reads `graphData.nodes` which is `undefined`.

**Fix in `App.tsx`:**
```tsx
const handleUpload = (responseData: any) => {
  setGraphData({
    ...responseData.graph_json,
    model_name: responseData.model_name,
    framework: responseData.framework,
    total_params: responseData.total_params,
  })
}
```

---

### BUG-03: `en.json` is not valid JSON

**File:** `config/languages/en.json`

**Problem:** File uses YAML syntax (no braces, unquoted keys) but has `.json` extension.

**Fix:** Convert to proper JSON:
```json
{
  "layers": {
    "Conv": "Convolutional layer — extracts spatial features",
    "Relu": "ReLU activation — outputs max(0, x)"
  },
  "analysis": {
    "CRITICAL": "Critical issue",
    "WARNING": "Warning",
    "INFO": "Information"
  },
  "ui": {
    "upload": "Upload Model",
    "analyze": "Analyze"
  }
}
```

---

### BUG-04: Missing `tsconfig.node.json`

**File:** `frontend/tsconfig.json` references it but file doesn't exist.

**Fix:** Create `frontend/tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

---

### BUG-05: FLOPs MatMul double-counts batch

**File:** `src/analysis/flops.py`, `_matmul_flops` function

**Problem:** For 2D input `[M, K]`, sets both `batch = M` and `m = M`, resulting in `2 * M * M * K * N` instead of `2 * M * K * N`.

**Fix:**
```python
def _matmul_flops(input_shape: list, output_shape: list) -> int:
    if len(input_shape) < 2 or len(output_shape) < 2:
        return 0
    # For 2D: [M, K] -> [M, N], FLOPs = 2 * M * K * N
    # For 3D: [B, M, K] -> [B, M, N], FLOPs = 2 * B * M * K * N
    if len(input_shape) == 2:
        m, k = input_shape
        n = output_shape[-1]
        return 2 * m * k * n
    else:
        batch = input_shape[0]
        m = input_shape[-2]
        k = input_shape[-1]
        n = output_shape[-1]
        return 2 * batch * m * k * n
```

---

### BUG-06: Stride detection broken

**File:** `src/analysis/rules/efficiency_rules.py`

**Problem:** `n.attributes.get("strides", [1]) != [1]` — comparing `[1, 1] != [1]` is always `True`.

**Fix:**
```python
strides = n.attributes.get("strides", [1])
has_strided_conv = any(s > 1 for s in strides)
```

---

## 📊 Current State Summary

| Component | Status | What's Done | What's Missing |
|-----------|--------|-------------|----------------|
| **ONNX Parser** | ✅ 90% | Full protobuf parsing, shapes, weights, edges | `connections_in/out` not populated on nodes |
| **Graph Model** | ✅ 85% | All dataclasses complete | builder.py, skip_detector.py, group.py, classifier.py |
| **Analysis Engine** | ✅ 70% | 11 rules working, memory estimator | task_rules.py (18 rules), model_card.py |
| **FLOPs Calculator** | ⚠️ 60% | Most layer types covered | MatMul bug, stride bug |
| **API Routes** | ⚠️ 40% | All 4 routes defined | graph_store sharing, export/compare stubs |
| **Frontend** | ⚠️ 50% | All components exist, styling done | Data shape bugs, API wiring |
| **Export** | ❌ 10% | Route exists as stub | All 4 exporters missing |
| **Config** | ⚠️ 60% | analysis_rules.yaml + layer_shapes.yaml | en.json broken, 4 language files missing |
| **Tests** | ⚠️ 60% | 20 test cases | Some bugs, missing edge cases |
| **Docker** | ✅ 80% | Both Dockerfiles + compose | Missing tsconfig.node.json blocks frontend build |
| **Competition** | ⚠️ 40% | Registration + timeline + essay outline | 800-word essay needs writing |
| **Research** | ✅ 100% | 198KB across 5 reports | Nothing |

**Overall: ~35% complete. Solid foundation, needs wiring and implementation.**

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** — web framework
- **ONNX** (onnx library) — model parsing
- **Pydantic** — data validation
- **NumPy** — numerical operations
- **Trimesh** — 3D export (GLB/GLTF)
- **ReportLab** — PDF export
- **PyYAML** — config parsing

### Frontend
- **React 18** + **TypeScript**
- **Three.js** + **@react-three/fiber** + **@react-three/drei** — 3D rendering
- **Vite** — build tool
- **Zustand** — state management
- **Axios** — HTTP client
- **Lucide React** — icons

### Infrastructure
- **Docker** + **docker-compose**
- **GitHub Actions** (planned) — CI/CD

---

## 🧩 How to Add a New Analysis Rule

1. **Choose the rule category:** `layer_rules.py`, `architecture_rules.py`, `efficiency_rules.py`, or create `task_rules.py`

2. **Add a method to the rules class:**
```python
def _check_my_new_rule(self, graph: NeuroScopeGraph) -> list[Finding]:
    findings = []
    for node in graph.nodes:
        if <condition>:
            findings.append(Finding(
                severity="WARNING",        # CRITICAL, WARNING, or INFO
                rule_id="LAYER_005",       # Unique ID
                title="Short Title",
                message="Detailed explanation of the problem.",
                fix="Suggested fix.",
                layer_ids=[node.id],       # Affected layers
                category="layer",          # layer, architecture, efficiency, task
            ))
    return findings
```

3. **Register it in the `check()` method:**
```python
def check(self, graph: NeuroScopeGraph) -> list[Finding]:
    findings = []
    findings.extend(self._check_my_new_rule(graph))
    # ... other rules
    return findings
```

4. **Add a test in `tests/test_analysis/test_rules.py`:**
```python
def test_my_new_rule(self):
    nodes = [_make_node(0, "SomeOp", "some_category")]
    graph = _make_graph(nodes)
    findings = self.rules.check(graph)
    assert any(f.rule_id == "LAYER_005" for f in findings)
```

---

## 🧩 How to Add a New Parser

1. **Create `src/parsers/my_parser.py`:**
```python
from src.parsers import BaseParser
from src.graph import NeuroScopeGraph

class MyParser(BaseParser):
    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith(".myext")

    def parse(self, file_path: str, **kwargs) -> NeuroScopeGraph:
        # Parse the file
        # Build LayerNode list
        # Build Edge list
        # Return NeuroScopeGraph
        pass
```

2. **Register it in `src/api/routes/upload.py`:**
```python
from src.parsers.my_parser import MyParser
PARSERS = [ONNXParser(), MyParser()]
```

---

## 🧩 How to Add a New Frontend Component

1. **Create `frontend/src/components/MyComponent.tsx`:**
```tsx
interface MyComponentProps {
  data: any
  onAction: (result: any) => void
}

export default function MyComponent({ data, onAction }: MyComponentProps) {
  return (
    <div className="my-component">
      {/* Your UI */}
    </div>
  )
}
```

2. **Add styles in `frontend/src/index.css`:**
```css
.my-component {
  /* Your styles */
}
```

3. **Import in `App.tsx` and use it.**

---

## 🧩 How to Add a New Export Format

1. **Create `src/export/my_exporter.py`:**
```python
def export_to_my_format(graph, analysis_report, output_path):
    """Export model visualization to MyFormat."""
    # Generate the output
    pass
```

2. **Wire it in `src/api/routes/export.py`:**
```python
from src.export.my_exporter import export_to_my_format

# In the export endpoint:
elif request.format == "myformat":
    content = export_to_my_format(graph, report)
    return StreamingResponse(...)
```

---

## 🎯 Competition Context

**Competition:** Presidential African Youth in AI and Robotics Competition 2026 (AYAIR)
**Category:** Education Enhancement
**Deadline:** June 30, 2026, 21:45 GMT (submission of essay + registration)
**Finalists:** September 17, 2026
**Finals:** October 12-13, 2026 (Egypt)

**Judging criteria:**
- Innovation — Is it new and unique?
- Functionality — Does it work?
- Impact — Does it solve a real African educational challenge?

**Key narrative:** NeuroScope is a free, offline-capable, browser-based ML education tool designed for Africa's constraints — low bandwidth, low hardware, multilingual users.

---

## 🚀 Quick Start for Developers

```bash
# Clone
git clone https://github.com/hazemelerefey/neuroscope.git
cd neuroscope

# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd src && uvicorn main:app --reload  # Runs on http://localhost:8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000

# Docker (alternative)
docker-compose up --build
```

---

## 📝 Notes for AI Agents

- **Don't break existing working code** — the ONNX parser and graph model are solid. Build on top.
- **The `graph_store` bug is the #1 priority** — nothing works end-to-end without it.
- **Frontend data shape mismatch is #2** — UI is completely broken without this fix.
- **Check `docs/code_review.md`, `docs/frontend_review.md`, and `docs/project_review.md`** for the full list of issues.
- **The research reports in `research/`** contain detailed technical specs for everything — ONNX schema, FLOPs formulas, anti-pattern detection logic, etc.
- **The competition essay (`competition/essay_draft.md`)** needs to be written as a full 800-word PDF. This is urgent — deadline is June 30.
- **When adding features, write tests** — test coverage is currently low.
- **Use the existing data models** — `LayerNode`, `Edge`, `Finding`, `AnalysisReport`, `NeuroScopeGraph` in `src/graph/__init__.py`. Don't create new ones.
- **The analysis rules YAML config** (`config/analysis_rules.yaml`) defines thresholds. Use it instead of hardcoding values.

---

*Last updated: 2026-06-25*
