# NeuroScope — Comprehensive Project Review

> **Audit Date:** 2026-06-25
> **Auditor:** Senior ML Engineer / Project Architect
> **Scope:** Full project structure, code, documentation, competition readiness

---

## Executive Summary

NeuroScope is an ambitious and well-conceived project — a web-based 3D neural network architecture visualizer and analyzer targeting African ML students. The **concept is strong**, the **architecture design is sound**, and the **research is thorough**. However, the project is currently a **skeleton with critical gaps** that prevent it from running. It needs focused work on wiring components together, implementing missing modules, and completing competition materials.

**Overall Maturity: ~35% complete (solid foundation, significant implementation gaps)**

---

## 1. Project Structure Assessment

### ✅ What's Good

- **Clean directory layout** — follows the architecture design from `docs/architecture_brainstorm.md`
- **Proper Python package structure** — `__init__.py` files present in all Python packages
- **Separation of concerns** — parsers, analysis, graph, API routes are well-separated
- **Dataclass-based graph model** — `NeuroScopeGraph`, `LayerNode`, `Edge`, `Finding`, `AnalysisReport` are well-designed
- **ONNX parser is complete and functional** — properly parses nodes, edges, shapes, weights
- **Analysis rules are well-implemented** — 11 rules with clear messages and fixes
- **Test suite exists** — unit tests for graph, FLOPs, rules, and parser
- **Docker setup exists** — both Dockerfiles and docker-compose.yml
- **i18n started** — English language file exists with layer descriptions

### ❌ Critical Structural Issues

| # | Issue | Severity |
|---|-------|----------|
| 1 | **`graph_store` is not shared between routes** — `upload.py` and `analyze.py` each have separate module-level stores. Uploaded models can never be analyzed. | 🔴 CRITICAL |
| 2 | **`src/export/` is empty** — No export implementations exist. The export route is a stub. | 🔴 CRITICAL |
| 3 | **`src/utils/` is empty** — No shared utility code | 🟡 MEDIUM |
| 4 | **13 empty directories** — placeholders with no files | 🟡 MEDIUM |
| 5 | **`config/languages/en.json` is NOT valid JSON** — it's YAML syntax in a `.json` file (uses `:` without quotes, no braces) | 🔴 CRITICAL |
| 6 | **`tsconfig.json` references missing `tsconfig.node.json`** — TypeScript build will fail | 🔴 CRITICAL |

---

## 2. Missing Files Audit

### 🔴 Missing — Blocks Functionality

| File | Referenced By | Impact |
|------|--------------|--------|
| `frontend/tsconfig.node.json` | `frontend/tsconfig.json` line 20 | TypeScript build fails |
| `frontend/public/neuroscope.svg` | `frontend/index.html` line 5 | 404 for favicon |
| `CONTRIBUTING.md` | `README.md` line 156 | Broken link |
| `src/export/glb_exporter.py` | Architecture docs, README | No GLB export |
| `src/export/svg_exporter.py` | Architecture docs, README | No SVG export |
| `src/export/pdf_exporter.py` | Architecture docs, README | No PDF export |
| `src/export/markdown_exporter.py` | Architecture docs, README | No real MD export |
| `src/graph/__init__.py` content | `src/parsers/__init__.py`, all analysis code | Only has dataclasses, missing builder/skip_detector |
| `data/samples/*.onnx` | Tests, README | No sample models for testing |
| `config/languages/fr.json` | README claims multilingual | Only English exists |
| `config/languages/ar.json` | README claims multilingual | Only English exists |
| `config/languages/sw.json` | README claims multilingual | Only English exists |
| `config/languages/pt.json` | README claims multilingual | Only English exists |
| `package-lock.json` | `Dockerfile.frontend` | Docker build may use wrong dependency versions |

### 🟡 Missing — Expected for Completeness

| File | Purpose |
|------|---------|
| `src/parsers/pytorch_parser.py` | Parse .pt/.pth files |
| `src/parsers/keras_parser.py` | Parse .h5/.keras files |
| `src/parsers/tflite_parser.py` | Parse .tflite files |
| `src/analysis/rules/task_rules.py` | Task-specific rules (18 planned) |
| `src/analysis/model_card.py` | Auto model card generator |
| `src/graph/builder.py` | Graph construction from parsed data |
| `src/graph/skip_detector.py` | Skip/residual connection detection |
| `src/graph/group.py` | Layer pattern grouping |
| `src/graph/classifier.py` | Architecture type detection |
| `frontend/src/hooks/useModelUpload.ts` | Upload hook |
| `frontend/src/hooks/useThreeScene.ts` | Three.js scene hook |
| `frontend/src/hooks/useAnalysis.ts` | Analysis hook |
| `frontend/src/three/shapes.ts` | Shape mapping |
| `frontend/src/three/colors.ts` | Color mapping |
| `frontend/src/three/layout.ts` | Node positioning |
| `frontend/src/three/edges.ts` | Edge rendering |
| `frontend/src/three/animation.ts` | Forward pass animation |
| `frontend/src/utils/api.ts` | API client |
| `frontend/src/utils/format.ts` | Number formatting |
| `frontend/src/components/LayerPanel.tsx` | Layer detail view |
| `frontend/src/components/CompareView.tsx` | Model comparison |
| `frontend/src/components/ModelCard.tsx` | Model card display |
| `tests/test_export/test_glb_exporter.py` | Export tests |
| `tests/test_export/test_pdf_exporter.py` | Export tests |
| `tests/test_graph/test_builder.py` | Builder tests |
| `tests/test_graph/test_skip_detector.py` | Skip detection tests |

---

## 3. Code-Level Bugs & Issues

### 🔴 Critical Bugs

#### Bug 1: `graph_store` Not Shared Between Upload and Analyze Routes

**Location:** `src/api/routes/upload.py` and `src/api/routes/analyze.py`

```python
# upload.py — does NOT populate any shared store
# The parsed graph is serialized and returned, but never stored

# analyze.py — has its own separate store
graph_store: dict[str, NeuroScopeGraph] = {}  # Always empty!
```

**Impact:** The `/api/analyze` endpoint will ALWAYS return 404 because no graph is ever stored in its `graph_store`. The entire analysis pipeline is broken.

**Fix:** Create a shared store (e.g., in `src/api/deps.py` or `src/api/store.py`) and import it in both routes. The upload route must store the graph after parsing.

#### Bug 2: `en.json` Is Not Valid JSON

**Location:** `config/languages/en.json`

The file uses YAML syntax (`layers:` with unquoted keys) but has a `.json` extension. Any JSON parser will fail.

**Fix:** Either convert to valid JSON (add braces, quote all keys) or rename to `.yaml`.

#### Bug 3: Missing `tsconfig.node.json`

**Location:** `frontend/tsconfig.json` line 20

```json
"references": [{ "path": "./tsconfig.node.json" }]
```

This file doesn't exist. `tsc` will fail.

**Fix:** Create the file or remove the `references` field.

#### Bug 4: ONNX Parser Test References `BaseParser` Without Import

**Location:** `tests/test_parsers/test_onnx_parser.py` line 27

```python
assert BaseParser.detect_format("model.onnx") == "onnx"
```

`BaseParser` is never imported. This test will fail with `NameError`.

**Fix:** Add `from src.parsers import BaseParser` at the top.

#### Bug 5: Docker Compose Frontend Build Context Mismatch

**Location:** `docker-compose.yml`

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: ../docker/Dockerfile.frontend
```

The `context` is `./frontend` but the Dockerfile copies from the context root. The `Dockerfile.frontend` expects to copy `package.json` and source from the frontend directory, which is correct. However, the `..` in the dockerfile path may cause issues with some Docker Compose versions. More importantly, the Dockerfile doesn't copy `tsconfig.json`, `vite.config.ts`, or `index.html` explicitly — it relies on `COPY . .` which will work from the context.

**Verdict:** This will likely work but is fragile. Consider using a single context with explicit paths.

#### Bug 6: Canvas3D Has Unused Imports

**Location:** `frontend/src/components/Canvas3D.tsx` line 1

```typescript
import { useRef, useEffect } from 'react'
```

`useRef` and `useEffect` are imported but never used. With `noUnusedLocals: true` in tsconfig, this will cause a TypeScript compilation error.

### 🟡 Moderate Issues

| Issue | Location | Description |
|-------|----------|-------------|
| Hardcoded `CONTRIBUTING.md` link | README.md line 156 | File doesn't exist |
| `version: "3.9"` in docker-compose.yml | docker-compose.yml | Deprecated in modern Docker Compose (v2+) |
| No `__init__.py` in `tests/` | `tests/` | pytest may have import issues depending on config |
| No `.env.example` | Root | No template for environment variables |
| No `pyproject.toml` or `setup.py` | Root | Python package isn't installable |
| Export route is entirely stubbed | `src/api/routes/export.py` | Only returns placeholder text |
| Compare route returns failure | `src/api/routes/compare.py` | Always returns `success=False` |
| No CORS origin restriction | `src/main.py` | `allow_origins=["*"]` is fine for dev but noted |
| FLOPs test assertion may be wrong | `tests/test_analysis/test_flops.py` line 32 | `assert flops == 2 * 1 * 512 * 256` — the `_matmul_flops` function uses `2 * batch * m * k * n` where batch=1, m=1 (from input[-2] when len=2), k=512, n=256. But `m` calculation: `input_shape[-2] if len(input_shape) > 2 else input_shape[0]` → len=2, so m=input_shape[0]=1. Result: 2*1*1*512*256 = 262,144. Test expects 2*1*512*256 = 262,144. ✓ Actually correct. |

---

## 4. Documentation Review

### README.md

| Aspect | Status | Notes |
|--------|--------|-------|
| Project description | ✅ Good | Clear, compelling pitch |
| Feature table | ⚠️ Overpromises | Claims 47+ rules, multilingual, universal format — none fully implemented |
| Quick start | ⚠️ Broken | `cd backend && uvicorn main:app` — there's no `backend/` directory, it's `src/` |
| Project structure | ✅ Accurate | Matches actual layout |
| Architecture diagram | ✅ Good | ASCII art pipeline is clear |
| Competition section | ✅ Good | Category rationale is strong |
| Timeline | ✅ Realistic | Phased approach makes sense |
| Links | ❌ Broken | `CONTRIBUTING.md` doesn't exist |

### competition/essay_draft.md

| Aspect | Status | Notes |
|--------|--------|-------|
| Structure | ✅ Good | 8-section outline is well-organized |
| Content | ⚠️ Incomplete | Still an outline, not a full 800-word essay |
| Placeholders | ❌ Many | Team name, project name, team details all TBD |
| Word count | ❌ Not ready | Needs to be written and trimmed to 800 words |
| PDF conversion | ❌ Not done | Needs to be converted to PDF for submission |

### competition/registration.md

| Aspect | Status | Notes |
|--------|--------|-------|
| Form fields mapped | ✅ Good | All Jotform fields listed |
| Placeholders | ❌ All | Every field is `[YOUR NAME]`, `[YOUR EMAIL]`, etc. |
| Category rationale | ✅ Strong | Well-argued for Education Enhancement |
| Post-submission checklist | ✅ Good | Clear action items |

### competition/timeline.md

| Aspect | Status | Notes |
|--------|--------|-------|
| Dates | ✅ Accurate | Matches competition schedule |
| Milestones | ✅ Realistic | Phased development plan |

### docs/architecture_brainstorm.md

| Aspect | Status | Notes |
|--------|--------|-------|
| Competitor analysis | ✅ Excellent | Deep dive into modelviz-ai internals |
| Technical design | ✅ Thorough | Complete pipeline design |
| Differentiation | ✅ Clear | 16-point comparison table |
| Phase planning | ✅ Good | 4-phase development roadmap |

---

## 5. Configuration Review

### config/analysis_rules.yaml ✅

- Well-structured with layer, architecture, and efficiency rule sections
- Hardware presets for T4, V100, A100, RTX3090, RTX4090, CPU
- Thresholds are reasonable
- **Gap:** No `task_rules` section (planned but not implemented)

### config/layer_shapes.yaml ✅

- Complete mapping of 11 layer categories to 3D shapes
- Edge styles defined (sequential, skip, residual, concat)
- Colors are consistent with frontend code
- **Note:** Frontend `Canvas3D.tsx` duplicates this mapping instead of loading from config

### config/languages/en.json ❌

- **Not valid JSON** — uses YAML syntax in a .json file
- Should be either valid JSON or renamed to `.yaml`
- Only English exists; 4 more languages needed for multilingual claim

### requirements.txt ✅

- Core dependencies are pinned
- PyTorch and TensorFlow are correctly marked as optional
- Missing: `pytest` (for running tests), `httpx` (for FastAPI test client)

### frontend/package.json ✅

- Dependencies are reasonable (React, Three.js, Zustand, Axios)
- Scripts are standard Vite setup
- Missing: `package-lock.json` for reproducible builds

---

## 6. Docker Review

### docker/Dockerfile.backend ✅ (mostly)

- Uses Python 3.11-slim (good)
- Installs build-essential (needed for some pip packages)
- Copies `src/` and `config/`
- **Issue:** Doesn't copy `requirements.txt` before installing — wait, it does. ✅
- **Issue:** Doesn't copy `data/` directory (but it's mounted via docker-compose)

### docker/Dockerfile.frontend ⚠️

- Uses node:20-alpine (good)
- Runs `npm install` then `npm run dev`
- **Issue:** Dev server in production — should use `npm run build` + nginx for production
- **Issue:** No `.dockerignore` — will copy `node_modules/` if present locally

### docker-compose.yml ⚠️

- Services are properly defined
- Volume mounts for `data/` and `config/`
- **Issue:** `version: "3.9"` is deprecated in Docker Compose v2+
- **Issue:** Frontend `VITE_API_URL` uses `http://backend:8000` but Vite env vars need `VITE_` prefix to be exposed to client — this is correct ✅
- **Issue:** No health checks
- **Issue:** No network definition (relies on default)

---

## 7. Competition Readiness

### Submission Deadline: June 30, 2026, 21:45 GMT

| Item | Status | Action Needed |
|------|--------|---------------|
| Jotform submission | ❌ Not ready | All personal fields are placeholders |
| Project Introduction Essay | ❌ Not written | Only outline exists, needs full 800-word essay |
| Essay as PDF | ❌ Not created | Write essay → convert to PDF |
| Project name | ❌ Not decided | "NeuroScope" is a working name |
| Team details | ❌ Not filled | Need names, emails, institutions |
| Demo prototype | ⚠️ Partial | Backend parses ONNX, frontend has 3D viz, but they're not wired together |
| Full project paper | ❌ Not started | For reply to acknowledgement email |

### What CAN Be Shown by June 30

If the critical bugs are fixed (especially the graph_store wiring), the following demo flow would work:
1. Upload an ONNX file → backend parses it → returns graph JSON
2. Frontend renders 3D visualization of the architecture
3. Click "Analyze" → backend runs 11 rules → shows health score + findings
4. Export as Markdown (placeholder)

---

## 8. TOP 5 Most Critical Fixes

### 🔴 1. Wire Up the Shared Graph Store (Blocks ALL Functionality)

**Problem:** Upload and analyze routes have separate stores. Nothing works end-to-end.

**Fix:**
```python
# Create src/api/store.py
from src.graph import NeuroScopeGraph
graph_store: dict[str, NeuroScopeGraph] = {}

# In upload.py and analyze.py:
from src.api.store import graph_store
```

Upload route must populate the store after parsing. This is the single most critical bug — without it, the app is completely non-functional.

### 🔴 2. Fix `en.json` → Valid JSON (Blocks i18n Loading)

**Problem:** YAML syntax in a `.json` file. Any JSON parser fails.

**Fix:** Convert to proper JSON:
```json
{
  "layers": {
    "Conv": "Convolutional layer — extracts spatial features...",
    ...
  },
  "analysis": { ... },
  "ui": { ... }
}
```

### 🔴 3. Create `tsconfig.node.json` (Blocks Frontend Build)

**Problem:** Referenced but missing. `tsc` fails.

**Fix:** Create the file:
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

### 🔴 4. Write the Competition Essay (Blocks Submission)

**Problem:** Only an outline exists. The essay is required for submission.

**Fix:** Expand the outline into a full 800-word essay. Fill in team details. Convert to PDF. This is a hard deadline — June 30, 2026.

### 🟡 5. Implement Export Engine (Core Feature Missing)

**Problem:** `src/export/` is empty. Export route returns placeholders. README promises GLB, SVG, PDF, Markdown exports.

**Fix:** At minimum, implement:
- `markdown_exporter.py` — generate a text report from AnalysisReport (easiest, high value)
- `pdf_exporter.py` — use reportlab to generate a PDF report
- These are the two formats the export route already partially handles

---

## 9. Additional Recommendations

### Quick Wins (< 1 hour each)

1. **Fix the Quick Start in README** — change `cd backend && uvicorn main:app` to `uvicorn src.main:app`
2. **Add `__init__.py` to `tests/`** — ensures pytest can import test modules
3. **Remove unused imports in `Canvas3D.tsx`** — `useRef`, `useEffect` will cause TS errors
4. **Add `BaseParser` import in test** — `tests/test_parsers/test_onnx_parser.py` line 27
5. **Create a simple favicon** — add `frontend/public/neuroscope.svg`
6. **Remove `CONTRIBUTING.md` link** from README, or create the file
7. **Add `pytest` to requirements.txt** — needed to run tests

### Medium Effort (1-4 hours each)

1. **Create a shared API store** — fix the graph_store wiring
2. **Implement markdown exporter** — generate text reports from AnalysisReport
3. **Add sample ONNX model** — create a tiny CNN in PyTorch, export to ONNX, add to `data/samples/`
4. **Add missing language files** — at least stub `.json` files for fr, ar, sw, pt
5. **Add `.env.example`** — document required environment variables

### Higher Effort (4+ hours each)

1. **Implement PyTorch parser** — requires torch dependency, export to ONNX then parse
2. **Implement PDF exporter** — use reportlab for formatted reports
3. **Implement GLB exporter** — use trimesh to create 3D model files
4. **Complete the frontend hooks** — `useModelUpload`, `useThreeScene`, `useAnalysis`
5. **Layer grouping** — merge Conv+BN+ReLU patterns for cleaner visualization
6. **Write the full competition essay** — 800 words, polished, converted to PDF

---

## 10. What's Working Well

Despite the gaps, several things are **genuinely well-done**:

1. **The graph data model** (`NeuroScopeGraph`, `LayerNode`, `Edge`, `Finding`) is clean, extensible, and well-thought-out
2. **The ONNX parser** is production-quality — handles shape inference, weight extraction, attribute parsing, and edge detection
3. **The analysis rules** have excellent educational explanations — each finding tells the user *why* it's a problem and *how* to fix it
4. **The FLOPs calculator** handles Conv, MatMul, normalization, pooling, activation, and RNN layers correctly
5. **The memory estimator** accounts for weights, gradients, optimizer states, and activations
6. **The frontend UI** is well-designed with a clean dark theme, proper component structure, and good UX patterns
7. **The research** is thorough — 198KB of competitive analysis, tech stack evaluation, and architecture design
8. **The 3D shape mapping** is creative and educationally meaningful (spheres for activations, cylinders for recurrent, etc.)

---

## 11. Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Architecture & Design** | 8/10 | Excellent design, matches the brainstorm doc |
| **Backend Implementation** | 5/10 | Parser + analysis work, but not wired together |
| **Frontend Implementation** | 6/10 | Components exist, but hooks/utils missing |
| **Testing** | 5/10 | Tests exist for core modules, but many gaps |
| **Documentation** | 7/10 | README and architecture docs are strong |
| **Configuration** | 6/10 | YAML configs good, JSON i18n broken |
| **Docker** | 5/10 | Structure exists, needs production hardening |
| **Competition Readiness** | 2/10 | Essay not written, all fields are placeholders |
| **Code Quality** | 7/10 | Clean Python, proper dataclasses, good typing |
| **End-to-End Functionality** | 2/10 | Cannot run as a working application |

**Overall: 53/100** — Strong foundation, needs focused execution to become functional.

---

## 12. Recommended Action Plan (Priority Order)

### This Week (Before June 30)

1. ✅ Fix graph_store wiring (30 min)
2. ✅ Fix en.json format (15 min)
3. ✅ Create tsconfig.node.json (5 min)
4. ✅ Fix Canvas3D unused imports (2 min)
5. ✅ Fix test import for BaseParser (2 min)
6. ✅ Fix README quick start command (2 min)
7. ✅ Write the full 800-word competition essay (2 hours)
8. ✅ Fill in registration details (30 min)
9. ✅ Convert essay to PDF (15 min)
10. ✅ Submit to Jotform by June 30, 21:45 GMT

### July (Post-Submission)

1. Implement markdown exporter
2. Add sample ONNX model to `data/samples/`
3. Create shared API store properly
4. Add missing language files (stubs)
5. Implement PyTorch parser (export to ONNX path)
6. Add `pytest` and run full test suite

### August-September (Pre-Finals)

1. Implement PDF and GLB exporters
2. Complete frontend hooks and utilities
3. Add layer grouping and skip connection detection
4. Deploy web app
5. Create demo video

---

*Report generated by NeuroScope Project Review — 2026-06-25*
