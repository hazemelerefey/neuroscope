# NeuroScope Frontend Code Analysis

## 1. Frontend Architecture (React + Three.js + Vite)

### Stack Overview
- **React 18.3.1** with TypeScript
- **Three.js 0.169.0** via `@react-three/fiber` and `@react-three/drei`
- **Vite 5.4.0** as build tool with React plugin
- **Zustand 4.5.0** for state management
- **Axios 1.7.0** for HTTP requests
- **Lucide React 0.400.0** for icons

### Project Structure
```
neuroscope/frontend/
├── src/
│   ├── components/
│   │   ├── Canvas3D.tsx        # 3D visualization
│   │   ├── UploadZone.tsx      # File upload with drag/drop
│   │   ├── AnalysisPanel.tsx   # Model analysis UI
│   │   ├── LayerDetail.tsx     # Layer details panel
│   │   ├── StatsPanel.tsx      # Statistics display
│   │   └── ExportMenu.tsx      # Export functionality
│   ├── App.tsx                 # Main app component
│   ├── main.tsx                # Entry point
│   ├── store.ts                # Zustand state management
│   ├── types.ts                # TypeScript interfaces
│   └── index.css               # Global styles
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── nginx.conf
```

### Build & Development
- **Dev server**: Vite on port 3000 with API proxy to `http://localhost:8000`
- **Build**: `tsc && vite build`
- **API proxy**: `/api/*` requests forwarded to backend

---

## 2. 3D Visualization (Canvas3D.tsx)

### Three.js Rendering Approach

**Technology Stack:**
- `@react-three/fiber` - React renderer for Three.js
- `@react-three/drei` - Useful helpers (OrbitControls, PerspectiveCamera, Html, Line)

**Scene Setup:**
```typescript
<Canvas gl={{ antialias: true }} dpr={[1, 2]}>
  <PerspectiveCamera makeDefault position={[0, 5, 15]} />
  <OrbitControls enableDamping dampingFactor={0.05} />
  {/* Lighting */}
  <ambientLight intensity={0.5} />
  <directionalLight position={[10, 10, 5]} intensity={1} />
  <pointLight position={[-10, -10, -5]} intensity={0.5} />
  {/* Grid */}
  <gridHelper args={[50, 50, '#334155', '#1e293b']} />
</Canvas>
```

**Node Positioning:**
- Simple horizontal linear layout: `nodes.forEach((node, i) => [i * spacing - offset, 0, 0])`
- Spacing: 2.5 units between nodes
- No hierarchical or hierarchical layout algorithm

**Layer Visualization:**
- Each layer node rendered as a 3D mesh with category-specific geometry
- Geometry mapping via `LAYER_STYLES`:
  - Convolution: box
  - Linear: plane
  - Pooling: small cube
  - Activation: sphere
  - Normalization: slab
  - Reshape: cone
  - Regularization: wireframe
  - Recurrent: cylinder
  - Attention: octahedron
  - Combination: merge (default box)
- Colors mapped by category (e.g., convolution: #6366f1, activation: #f59e0b)
- Labels rendered as HTML overlays using `@react-three/drei`'s `<Html>` component

**Edge Rendering:**
- Sequential edges: straight lines in gray (#94a3b8)
- Skip connections: dashed lines in yellow (#f59e0b) with upward arc (quadratic bezier)
- Residual connections: solid lines in green (#10b981) with upward arc
- Curves computed manually using bezier interpolation

**Interactivity:**
- Click on layers to select and show details
- Orbit controls for camera rotation/zoom
- No hover effects or selection highlighting implemented

---

## 3. UI Components

### UploadZone.tsx
**Features:**
- Drag-and-drop file upload with visual feedback
- Click-to-browse file selection
- File validation:
  - Supported formats: `.onnx`, `.pt`, `.pth`, `.h5`, `.keras`, `.tflite`
  - Max file size: 500MB
- Upload progress bar with percentage
- Error handling with Axios
- Loading state with spinner

**UX Design:**
- Clean dashed border upload zone
- Drag state highlighting
- Progress indicator during upload
- Error messages with icon

### AnalysisPanel.tsx
**Features:**
- "Run Analysis" button to trigger model analysis
- Health score display with grade (A-F) and score (0-100)
- Findings list with severity filtering (CRITICAL, WARNING, INFO)
- Color-coded findings (red for critical, yellow for warnings, green for info)
- Clickable findings (logging layer IDs, no 3D highlighting)

**UX Design:**
- Gradient button for analysis trigger
- Visual health score card
- Filter tabs for severity
- Expandable findings with icons and descriptions

### LayerDetail.tsx
**Features:**
- Displays selected layer information
- Shows: name, type, category, parameters, description
- Input/output shapes in monospace format
- Close button to dismiss

**UX Design:**
- Purple border for emphasis
- Clean layout with icons
- Monospace formatting for shapes

### StatsPanel.tsx
**Features:**
- Displays model statistics:
  - Number of layers
  - Total parameters (formatted: K, M, B)
  - Framework
  - FLOPs (from analysis)
  - Memory usage (from analysis)
  - Architecture type (from analysis)

**UX Design:**
- Grid layout for stats
- Icons for each stat type
- Conditional display of analysis-only stats

### ExportMenu.tsx
**Features:**
- Export options: JSON, TXT, PNG
- Download functionality with blob handling
- Loading states per export format
- Error handling with blob response parsing

**UX Design:**
- Button list with icons
- Loading spinners per button
- Disabled state during export

---

## 4. State Management (store.ts)

**Zustand Store Structure:**
```typescript
interface NeuroScopeState {
  // Data
  graphData: GraphData | null
  analysisData: AnalysisReport | null
  selectedLayer: LayerNode | null

  // UI state
  isUploading: boolean
  error: string | null

  // Actions
  setGraphData: (data: GraphData) => void
  setAnalysisData: (data: AnalysisReport) => void
  selectLayer: (layer: LayerNode | null) => void
  setUploading: (v: boolean) => void
  setError: (e: string | null) => void
  reset: () => void
}
```

**Observations:**
- Simple, flat state structure
- No middleware (no devtools, persistence, or immer)
- Actions are straightforward setters
- `reset()` clears all state
- `isUploading` state exists but not used in App.tsx (UploadZone manages its own local state)

---

## 5. Types Definitions (types.ts)

**Key Interfaces:**
- `LayerNode`: Complete layer data including shapes, params, flops, connections
- `Edge`: Connection between layers with type (sequential, skip, residual, concat)
- `Finding`: Analysis finding with severity, rule_id, message, fix
- `AnalysisReport`: Complete analysis results with health score, findings, statistics
- `GraphData`: Unwrapped graph data from upload response
- `UploadResponse`: Raw API response with nested graph_json
- `AnalyzeRequest`: Simple model_id request body

**Observations:**
- Well-typed interfaces matching backend shapes
- Some redundancy between `GraphData` and `UploadResponse.graph_json`
- Type safety for edge types and severity levels not enforced (string unions)

---

## 6. Styling (index.css)

**Design System:**
- Dark theme with CSS variables
- Color palette:
  - Background: #0f172a (primary), #1e293b (secondary)
  - Text: #f8fafc (primary), #94a3b8 (secondary)
  - Accents: blue (#3b82f6), purple (#8b5cf6), green (#10b981), red (#ef4444), yellow (#f59e0b)
- Border radius: 8px
- Font: Inter, Segoe UI, system-ui

**Layout:**
- Flexbox-based responsive layout
- Fixed panel width: 360px
- Mobile responsive with column layout
- Canvas area fills remaining space

**Components:**
- Upload zone with hover/drag states
- Stats grid (2 columns)
- Health score card with grade circles
- Findings list with colored left borders
- Loading spinners with keyframe animation

**Responsive Design:**
- Breakpoint at 768px
- Stacks panels vertically on mobile
- Adjusts upload zone margins

---

## 7. Issues & Observations

### Architecture Issues

1. **No Error Boundaries**
   - No React error boundaries for 3D rendering errors
   - Three.js errors could crash the entire app

2. **State Management Redundancy**
   - `isUploading` in store not used by App.tsx
   - UploadZone manages its own upload state locally

3. **No Loading States in App**
   - No global loading indicator for API calls
   - Each component manages its own loading state

### 3D Visualization Issues

1. **Simple Linear Layout**
   - All nodes placed in a straight horizontal line
   - No hierarchical layout for complex architectures
   - No depth positioning for different layers

2. **No Selection Highlighting**
   - Clicking a layer doesn't highlight it in 3D
   - No visual feedback for selected layer

3. **Fixed Geometry Sizes**
   - All meshes use similar sizes regardless of parameters
   - No size scaling based on params/flops

4. **No Camera Animation**
   - No smooth transitions when selecting layers
   - No auto-focus on selected layer

5. **Edge Rendering**
   - Skip/residual curves use manual bezier calculation
   - No dynamic curve adjustment based on distance

### UI Issues

1. **No Responsive 3D Canvas**
   - Canvas doesn't adapt to mobile touch controls
   - No touch gesture support

2. **Export Format Limitations**
   - PNG export uses backend, not client-side rendering
   - No SVG export option

3. **Finding Interaction**
   - Clicking findings logs to console but doesn't highlight layers
   - No integration between analysis and 3D view

4. **No Keyboard Navigation**
   - No keyboard shortcuts for common actions
   - No tab navigation in 3D canvas

### Code Quality Issues

1. **Type Safety**
   - Edge types and severity levels are strings, not unions
   - Could use string literal types for better safety

2. **Performance**
   - No memoization of 3D geometries
   - No virtualization for large node lists

3. **Accessibility**
   - No ARIA labels on 3D canvas
   - No screen reader support for layer selection

### Missing Features

1. **No Undo/Redo**
   - No history for layer selection or analysis

2. **No Search/Filter**
   - No way to search layers by name/type
   - No filtering in 3D view

3. **No Comparison**
   - No side-by-side model comparison
   - No diff view between models

4. **No Collaboration**
   - No sharing functionality
   - No comments on layers

---

## Summary

**What's Implemented:**
- Complete React + Three.js + Vite frontend
- File upload with drag/drop and progress
- 3D visualization with category-specific geometries
- Layer selection and detail display
- Model statistics display
- Architecture analysis with health scoring
- Export to JSON/TXT/PNG
- Dark theme with responsive design

**UX Design:**
- Clean, modern dark interface
- Intuitive upload workflow
- Clear visual hierarchy
- Color-coded severity levels
- Responsive layout for mobile

**3D Rendering Approach:**
- React Three Fiber for declarative Three.js
- Simple linear layout with horizontal spacing
- Category-based geometry and color mapping
- Interactive orbit controls
- HTML overlays for labels

**Component Architecture:**
- Functional components with hooks
- Zustand for global state
- Axios for API calls
- Lucide icons for consistency
- CSS variables for theming

**Key Issues:**
- Simple linear layout doesn't scale for complex models
- No visual feedback for selections
- Limited interactivity between analysis and 3D view
- No error boundaries for robustness
- Some state management redundancy

The codebase is well-structured and functional, but could benefit from enhanced 3D layout algorithms, better selection feedback, and tighter integration between analysis and visualization.