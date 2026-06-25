# NeuroScope Frontend — Code Review Report

**Date:** 2026-06-25
**Scope:** All frontend files in `frontend/`
**Severity Scale:** 🔴 Critical · 🟠 High · 🟡 Medium · 🟢 Low

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | 3 |
| 🟠 High | 4 |
| 🟡 Medium | 5 |
| 🟢 Low | 4 |

---

## 🔴 Critical Issues

### C1. Data shape mismatch — `graphData.nodes` / `graphData.edges` are `undefined`

**Files:** `App.tsx`, `Canvas3D.tsx`, `StatsPanel.tsx`

The backend `UploadResponse` nests graph data inside a `graph_json` field:

```python
# backend: src/api/routes/upload.py
class UploadResponse(BaseModel):
    success: bool
    message: str
    model_name: str
    framework: str
    num_layers: int
    total_params: int
    graph_json: dict  # ← nodes/edges live HERE
```

But every frontend component accesses `graphData.nodes` and `graphData.edges` directly — which are `undefined`:

```tsx
// Canvas3D.tsx — BROKEN
const nodes = graphData?.nodes || []       // ← undefined, always []
const edges = graphData?.edges || []       // ← undefined, always []

// StatsPanel.tsx — BROKEN
{graphData?.nodes?.length || 0}            // ← always 0
```

**Fix — Option A (recommended):** Unwrap `graph_json` in `App.tsx` before passing to children:

```tsx
// App.tsx — inside the onUpload handler
const [graphData, setGraphData] = useState<any>(null)

const handleUpload = (responseData: any) => {
  // Merge top-level metadata with graph_json contents
  setGraphData({
    ...responseData.graph_json,
    model_name: responseData.model_name,
    framework: responseData.framework,
    total_params: responseData.total_params,
    num_layers: responseData.num_layers,
  })
}

// Then pass handleUpload to <UploadZone onUpload={handleUpload} />
```

**Fix — Option B:** Change every component to access `graphData.graph_json.nodes`, etc. — more invasive, not recommended.

---

### C2. `graph_store` never populated — `/api/analyze` always returns 404

**File:** `AnalysisPanel.tsx` (frontend), `src/api/routes/analyze.py` (backend)

The analyze route reads from an in-memory `graph_store`:

```python
# analyze.py
graph_store: dict[str, NeuroScopeGraph] = {}

@router.post("/analyze")
async def analyze_model(request: AnalyzeRequest):
    graph = graph_store.get(request.model_id)  # ← always None!
    if not graph:
        raise HTTPException(status_code=404, ...)
```

But the upload route **never writes** to this store. It creates the graph, serializes it, returns it, and discards it.

**Fix (backend):** After parsing in `upload.py`, store the graph:

```python
from src.api.routes.analyze import graph_store

# After parsing:
graph_store[graph.model_name] = graph
```

Or better — use a shared store module (e.g., `src/api/store.py`) imported by both routes.

**Impact on frontend:** The "Run Analysis" button will always fail with a 404 error. The error is silently caught (`console.error` only) — no user-facing error message is shown.

---

### C3. Missing `tsconfig.node.json` — TypeScript build fails

**File:** `tsconfig.json`

```json
{
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

This file does not exist. Running `tsc` (as the `build` script does: `"build": "tsc && vite build"`) will fail with:

```
error TS6053: File 'tsconfig.node.json' not found.
```

**Fix:** Create `tsconfig.node.json`:

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

Or remove the `references` line from `tsconfig.json` if Vite handles its own config compilation.

---

## 🟠 High Issues

### H1. Unused imports — TypeScript compilation errors

**File:** `Canvas3D.tsx`

```tsx
import { useRef, useEffect } from 'react'  // ← never used
```

With `noUnusedLocals: true` in `tsconfig.json`, this causes:

```
error TS6133: 'useRef' is declared but its value is never read.
error TS6133: 'useEffect' is declared but its value is never read.
```

**Fix:** Remove the unused imports:

```tsx
// Remove: import { useRef, useEffect } from 'react'
```

---

### H2. `selectedLayer` state is set but never rendered

**File:** `App.tsx`

```tsx
const [selectedLayer, setSelectedLayer] = useState(null)
// ...
<Canvas3D graphData={graphData} onLayerClick={setSelectedLayer} />
```

Clicking a layer in the 3D view sets state, but nothing displays the selected layer's details. This is a missing feature that users will expect.

**Fix:** Add a `LayerDetail` component or show selected layer info in the panel area:

```tsx
{selectedLayer && (
  <div className="layer-detail">
    <h3>{selectedLayer.name}</h3>
    <p>Type: {selectedLayer.display_type}</p>
    <p>Parameters: {selectedLayer.formatted_params}</p>
    <p>Category: {selectedLayer.category}</p>
    {selectedLayer.description && <p>{selectedLayer.description}</p>}
    <button onClick={() => setSelectedLayer(null)}>✕ Close</button>
  </div>
)}
```

---

### H3. Missing CSS classes — spinner and canvas-3d

**File:** `UploadZone.tsx` references `.upload-spinner` and `.spinner`:

```tsx
<div className="upload-spinner">
  <div className="spinner" />
```

**File:** `Canvas3D.tsx` references `.canvas-3d`:

```tsx
<div className="canvas-3d" style={{ width: '100%', height: '100%' }}>
```

None of these classes are defined in `index.css`. The spinner will be invisible (no animation), and the canvas div has no explicit height — it relies on the flex parent, but `.canvas-area` has no height set either.

**Fix — add to `index.css`:**

```css
/* Spinner */
.upload-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--accent-blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 3D Canvas */
.canvas-3d {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.canvas-area {
  flex: 1;
  position: relative;
  min-height: 0; /* prevent flex overflow */
}
```

---

### H4. Memory leak in `EdgeLine` — geometry recreated every render

**File:** `Canvas3D.tsx`

```tsx
function EdgeLine({ start, end, edgeType }: any) {
  const points = [new THREE.Vector3(...start), new THREE.Vector3(...end)]
  const lineGeometry = new THREE.BufferGeometry().setFromPoints(points)
  // ← new geometry object every render, never disposed
```

Every re-render creates a new `BufferGeometry` without disposing the old one. For models with many edges, this leaks GPU memory.

**Fix:** Use `useMemo`:

```tsx
function EdgeLine({ start, end, edgeType }: any) {
  const color = edgeType === 'residual' ? '#10b981' :
                edgeType === 'skip' ? '#f59e0b' : '#94a3b8'

  const lineGeometry = useMemo(() => {
    const points = [new THREE.Vector3(...start), new THREE.Vector3(...end)]
    return new THREE.BufferGeometry().setFromPoints(points)
  }, [start[0], start[1], start[2], end[0], end[1], end[2]])

  return (
    <line geometry={lineGeometry}>
      <lineBasicMaterial color={color} />
    </line>
  )
}
```

Add `useMemo` to the import: `import { useRef, useEffect, useMemo } from 'react'` (after removing unused refs per H1).

---

## 🟡 Medium Issues

### M1. No error feedback in `AnalysisPanel`

**File:** `AnalysisPanel.tsx`

```tsx
} catch (err: any) {
  console.error('Analysis failed:', err)  // ← silent failure
}
```

Users click "Run Analysis", it fails silently. No error state is shown.

**Fix:**

```tsx
const [error, setError] = useState<string | null>(null)

const handleAnalyze = async () => {
  setIsAnalyzing(true)
  setError(null)
  try {
    // ...existing code...
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
  } finally {
    setIsAnalyzing(false)
  }
}

// In JSX, after the button:
{error && <p className="error">{error}</p>}
```

---

### M2. No error feedback in `ExportMenu`

**File:** `ExportMenu.tsx`

```tsx
} catch (err) {
  console.error('Export failed:', err)  // ← silent failure
}
```

Same issue as M1. Users get no feedback when export fails.

**Fix:** Add error state and display:

```tsx
const [error, setError] = useState<string | null>(null)

const handleExport = async (format: string) => {
  setError(null)
  try {
    // ...existing code...
  } catch (err: any) {
    setError(err.response?.data?.detail || `Export to ${format} failed.`)
  }
}

// In JSX:
{error && <p className="error">{error}</p>}
```

---

### M3. No way to reset / upload a new model

**File:** `App.tsx`

Once a model is uploaded, there's no button or mechanism to go back to the upload view. Users must refresh the page.

**Fix:** Add a reset button in the header:

```tsx
<header className="app-header">
  <div className="header-content">
    <h1>🧠 NeuroScope</h1>
    <p>AI-Powered 3D Neural Network Architecture Visualizer & Analyzer</p>
  </div>
  {graphData && (
    <button className="reset-btn" onClick={() => {
      setGraphData(null)
      setAnalysisData(null)
      setSelectedLayer(null)
    }}>
      📁 New Model
    </button>
  )}
</header>
```

Add CSS:
```css
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.reset-btn {
  padding: 8px 16px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.reset-btn:hover {
  border-color: var(--accent-blue);
}
```

---

### M4. Docker proxy mismatch

**File:** `vite.config.ts`, `docker-compose.yml`

Vite dev server proxies `/api` to `http://localhost:8000`. In Docker, the frontend container runs Vite, but `localhost:8000` inside that container is NOT the backend — the backend is at `backend:8000` (Docker service name).

The `docker-compose.yml` sets `VITE_API_URL=http://backend:8000`, but the vite config ignores this env var.

**Fix — update `vite.config.ts`:**

```ts
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_URL || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
```

---

### M5. No responsive design — broken on mobile

**File:** `index.css`

The workspace uses a fixed layout:

```css
.workspace {
  display: flex;
  flex: 1;
  height: calc(100vh - 80px);
}

.panel-area {
  width: 360px;  /* fixed width */
}
```

On screens < 768px, the 3D canvas gets squeezed to near-zero width.

**Fix — add media queries:**

```css
@media (max-width: 768px) {
  .workspace {
    flex-direction: column;
    height: auto;
  }

  .canvas-area {
    height: 50vh;
    min-height: 300px;
  }

  .panel-area {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--border);
  }

  .upload-zone {
    margin: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## 🟢 Low Issues

### L1. `any` types everywhere — no type safety

**Files:** All `.tsx` files

Every component uses `any` for props and state:

```tsx
graphData: any
analysisData: any
onLayerClick: (layer: any) => void
```

This defeats the purpose of TypeScript. Define proper interfaces:

```tsx
// types.ts
interface GraphNode {
  id: number
  name: string
  op_type: string
  category: string
  input_shapes: number[][]
  output_shapes: number[][]
  params: number
  display_type: string
  formatted_params: string
  description: string
}

interface GraphEdge {
  source_id: number
  target_id: number
  edge_type: string
  label?: string
}

interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  model_name: string
  framework: string
  total_params: number
  total_flops: number
  architecture_type: string
}

interface AnalysisData {
  findings: Finding[]
  health_score: number
  health_grade: string
  critical_count: number
  warning_count: number
  info_count: number
  total_flops: number
  total_memory_mb: number
  architecture_type: string
}
```

---

### L2. Edge `key` uses array index

**File:** `Canvas3D.tsx`

```tsx
{edges.map((edge: any, i: number) => {
  // ...
  return <EdgeLine key={i} ... />
})}
```

Using index as key is acceptable here since edges are static and don't reorder, but a composite key is more robust:

```tsx
key={`${edge.source_id}-${edge.target_id}`}
```

---

### L3. Flat 3D layout — all nodes at Y=0

**File:** `Canvas3D.tsx`

```tsx
nodePositions[node.id] = [i * spacing - (nodes.length * spacing) / 2, 0, 0]
```

All nodes are placed on a single horizontal line. The 3D view is effectively 2D. Consider using the node category or layer depth to vary Y/Z positions:

```tsx
const categoryOffsets: Record<string, number> = {
  convolution: 0,
  linear: 1,
  pooling: -1,
  activation: 2,
  normalization: -2,
}

nodes.forEach((node: any, i: number) => {
  const yOffset = categoryOffsets[node.category] || 0
  nodePositions[node.id] = [
    i * spacing - (nodes.length * spacing) / 2,
    yOffset * 1.5,
    0,
  ]
})
```

---

### L4. No `antialias` on Canvas

**File:** `Canvas3D.tsx`

The `<Canvas>` has no renderer settings. Add antialiasing for smoother edges:

```tsx
<Canvas gl={{ antialias: true }} dpr={[1, 2]}>
```

---

## Configuration Issues

### T1. `tsconfig.json` — strict mode flags will surface all above issues

The config enables `noUnusedLocals` and `noUnusedParameters`, which means H1 (unused imports) will block `tsc` and therefore `npm run build`. This is correct behavior — the flags are doing their job. Fix H1 first.

### T2. `package.json` — dependencies look complete

All required packages are present:
- ✅ `react`, `react-dom` — core
- ✅ `@react-three/fiber`, `@react-three/drei`, `three` — 3D rendering
- ✅ `zustand` — state management (declared but unused in current code)
- ✅ `axios` — HTTP client
- ✅ `lucide-react` — icons (declared but unused in current code)
- ✅ TypeScript, Vite, ESLint — dev tooling

Note: `zustand` and `lucide-react` are installed but never imported. Consider removing if not planned for use, or use them (zustand for state management would be better than prop-drilling).

### T3. `vite.config.ts` — proxy config is correct for local dev

`/api` → `http://localhost:8000` is correct assuming the FastAPI backend runs on port 8000. See M4 for Docker fix.

---

## API Integration Summary

| Frontend Call | Backend Route | Match? | Notes |
|---|---|---|---|
| `POST /api/upload` (multipart) | `POST /api/upload` (UploadFile) | ✅ | Works, but response shape causes C1 |
| `POST /api/analyze` (`{model_id}`) | `POST /api/analyze` (AnalyzeRequest) | ⚠️ | Endpoint matches, but always 404 due to C2 |
| `POST /api/export` (`{model_id, format}`) | `POST /api/export` (ExportRequest) | ✅ | Endpoint matches, but export is mostly TODO |

---

## Priority Fix Order

1. **C1** — Fix data shape mismatch (unwrapping `graph_json`) — nothing renders without this
2. **C3** — Create `tsconfig.node.json` — build fails without this
3. **H1** — Remove unused imports — `tsc` fails without this
4. **C2** — Fix backend `graph_store` population — analysis feature is completely broken
5. **H3** — Add missing CSS classes — spinner invisible, canvas may collapse
6. **H4** — Fix EdgeLine memory leak
7. **M1/M2** — Add error feedback UI
8. **M3** — Add reset button
9. **M4** — Fix Docker proxy
10. **M5** — Add responsive CSS
11. **L1–L4** — Type safety, key props, layout improvements, antialiasing
