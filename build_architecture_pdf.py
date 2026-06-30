#!/usr/bin/env python3
"""
NeuroScope Project Architecture PDF — Visual folder structure explanation
Uses pdf.co API for professional rendering.
"""

import os
import requests
import sys

PDFCO_API_KEY = os.environ.get("PDFCO_API_KEY", "hazemelerefy@gmail.com_Zjm0ugdruJYHBoDKaykaEpIkye19lcmSG7wGHvZQFFNPY2g9y9xYrxcFT5nUrPBQ")
OUTPUT_PDF = "docs/NeuroScope_Project_Architecture.pdf"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NeuroScope — Project Architecture</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', sans-serif;
    color: #1a1a2e;
    line-height: 1.7;
    font-size: 10.5pt;
    background: #fff;
  }

  /* Cover */
  .cover {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 80px 60px;
    page-break-after: always;
  }

  .cover-label {
    font-size: 9pt;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #6c6c8a;
    margin-bottom: 24px;
  }

  .cover-title {
    font-size: 44pt;
    font-weight: 700;
    color: #1a1a2e;
    letter-spacing: -1px;
    margin-bottom: 8px;
  }

  .cover-subtitle {
    font-size: 13pt;
    font-weight: 400;
    color: #6c6c8a;
    margin-bottom: 48px;
  }

  .cover-line {
    width: 60px;
    height: 2px;
    background: #1a1a2e;
    margin: 0 auto 48px;
  }

  .cover-meta {
    font-size: 10pt;
    color: #6c6c8a;
    line-height: 2;
  }

  .cover-meta strong {
    color: #1a1a2e;
    font-weight: 600;
  }

  /* Page */
  .page {
    max-width: 800px;
    margin: 0 auto;
    padding: 56px 64px;
  }

  /* Typography */
  h1 {
    font-size: 18pt;
    font-weight: 700;
    color: #1a1a2e;
    margin: 40px 0 20px;
    padding-bottom: 10px;
    border-bottom: 1.5px solid #e0e0e0;
  }
  h1:first-child { margin-top: 0; }

  h2 {
    font-size: 12pt;
    font-weight: 600;
    color: #1a1a2e;
    margin: 28px 0 12px;
  }

  p {
    margin-bottom: 14px;
    text-align: justify;
    hyphens: auto;
  }

  strong { font-weight: 600; }

  /* Folder tree */
  .tree {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9pt;
    line-height: 1.8;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 20px 24px;
    margin: 16px 0;
    white-space: pre;
  }

  .tree .folder { color: #3b82f6; font-weight: 600; }
  .tree .file { color: #1a1a2e; }
  .tree .desc { color: #64748b; font-family: 'Inter', sans-serif; font-size: 8.5pt; }

  /* File cards */
  .file-card {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 10px 0;
    background: #fafbfc;
  }

  .file-card-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10pt;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 4px;
  }

  .file-card-desc {
    font-size: 9pt;
    color: #64748b;
    margin: 0;
  }

  /* Callout */
  .callout {
    padding: 16px 20px;
    border-left: 3px solid #1a1a2e;
    margin: 16px 0;
    background: #fafafa;
  }

  .callout-title {
    font-size: 10pt;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 4px;
  }

  .callout p {
    font-size: 9.5pt;
    color: #64748b;
    margin: 0;
  }

  /* Flow diagram */
  .flow {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 20px 0;
    flex-wrap: wrap;
    justify-content: center;
  }

  .flow-step {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: center;
    min-width: 100px;
  }

  .flow-step-label {
    font-size: 9pt;
    font-weight: 600;
    color: #1a1a2e;
  }

  .flow-step-desc {
    font-size: 7.5pt;
    color: #64748b;
  }

  .flow-arrow {
    font-size: 16pt;
    color: #94a3b8;
  }

  /* Table */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 9.5pt;
  }

  th {
    background: #1a1a2e;
    color: #fff;
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 10px 14px;
    text-align: left;
  }

  td {
    padding: 10px 14px;
    border-bottom: 1px solid #eee;
  }

  tr:nth-child(even) { background: #fafafa; }

  /* Footer */
  .footer {
    margin-top: 48px;
    padding-top: 16px;
    border-top: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    font-size: 8pt;
    color: #999;
  }

  .footer strong { color: #1a1a2e; }

  /* Utilities */
  .page-break { page-break-before: always; }

  @media print {
    body { font-size: 10pt; }
    .cover { page-break-after: always; }
    h1 { page-break-after: avoid; }
    .tree { page-break-inside: avoid; }
  }
</style>
</head>
<body>

<!-- ==================== COVER ==================== -->
<div class="cover">
  <div class="cover-label">Project Documentation</div>
  <div class="cover-title">NeuroScope</div>
  <div class="cover-subtitle">Architecture & Folder Structure Guide</div>
  <div class="cover-line"></div>
  <div class="cover-meta">
    <strong>Team:</strong> DigiNeurons<br>
    <strong>Version:</strong> 0.1.0<br>
    <strong>Date:</strong> June 2026
  </div>
</div>

<!-- ==================== PAGE 1: OVERVIEW ==================== -->
<div class="page">

<h1>Project Overview</h1>

<p>NeuroScope is a full-stack application with a <strong>Python backend</strong> (FastAPI) and a <strong>React frontend</strong> (Three.js). The backend parses neural network models and runs analysis. The frontend renders interactive 3D visualizations.</p>

<h2>How It Works</h2>

<div class="flow">
  <div class="flow-step">
    <div class="flow-step-label">Upload</div>
    <div class="flow-step-desc">Model file</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-label">Parse</div>
    <div class="flow-step-desc">Extract layers</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-label">Analyze</div>
    <div class="flow-step-desc">47+ rules</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-label">Visualize</div>
    <div class="flow-step-desc">3D rendering</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-label">Export</div>
    <div class="flow-step-desc">JSON/TXT/PNG</div>
  </div>
</div>

<h2>Top-Level Structure</h2>

<div class="tree"><span class="folder">neuroscope/</span>
├── <span class="folder">src/</span>                   <span class="desc">Python backend (FastAPI)</span>
├── <span class="folder">frontend/</span>              <span class="desc">React frontend (Three.js)</span>
├── <span class="folder">config/</span>                <span class="desc">Configuration files</span>
├── <span class="folder">tests/</span>                 <span class="desc">Test suite</span>
├── <span class="folder">docker/</span>                <span class="desc">Dockerfiles</span>
├── <span class="folder">docs/</span>                  <span class="desc">Documentation</span>
├── <span class="folder">research/</span>              <span class="desc">Technical research</span>
├── <span class="folder">competition/</span>           <span class="desc">AYAIR 2026 materials</span>
├── <span class="folder">scripts/</span>               <span class="desc">Utility scripts</span>
├── <span class="file">README.md</span>              <span class="desc">Project overview</span>
├── <span class="file">requirements.txt</span>       <span class="desc">Python dependencies</span>
├── <span class="file">docker-compose.yml</span>     <span class="desc">Docker orchestration</span>
└── <span class="file">LICENSE</span>                <span class="desc">MIT License</span></div>

<!-- ==================== PAGE 2: BACKEND ==================== -->
<div class="page-break"></div>
<h1>Backend — src/</h1>

<p>The backend is a <strong>FastAPI</strong> application. It handles model parsing, architecture analysis, and serves the API endpoints that the frontend consumes.</p>

<div class="tree"><span class="folder">src/</span>
├── <span class="file">main.py</span>                <span class="desc">FastAPI app entry point (CORS, routes, health check)</span>
├── <span class="file">store.py</span>               <span class="desc">In-memory graph store (shared state across routes)</span>
│
├── <span class="folder">parsers/</span>               <span class="desc">Model file parsers (one per format)</span>
│   ├── <span class="file">onnx_parser.py</span>     <span class="desc">ONNX parser — IMPLEMENTED</span>
│   ├── <span class="file">pytorch_parser.py</span>  <span class="desc">PyTorch parser — stub (TODO)</span>
│   ├── <span class="file">keras_parser.py</span>    <span class="desc">Keras/TF parser — stub (TODO)</span>
│   └── <span class="file">tflite_parser.py</span>   <span class="desc">TFLite parser — stub (TODO)</span>
│
├── <span class="folder">graph/</span>                 <span class="desc">Internal graph representation</span>
│   └── <span class="file">__init__.py</span>        <span class="desc">LayerNode, Edge, Finding, NeuroScopeGraph dataclasses</span>
│
├── <span class="folder">analysis/</span>              <span class="desc">Architecture analysis engine</span>
│   ├── <span class="file">flops.py</span>           <span class="desc">FLOPs calculator per layer</span>
│   ├── <span class="file">memory.py</span>          <span class="desc">Memory estimator + training time</span>
│   └── <span class="folder">rules/</span>             <span class="desc">Anti-pattern detection rules (47+ rules)</span>
│       ├── <span class="file">layer_rules.py</span>  <span class="desc">Layer-level rules (4 rules)</span>
│       ├── <span class="file">architecture_rules.py</span> <span class="desc">Architecture rules (4 rules)</span>
│       └── <span class="file">efficiency_rules.py</span>  <span class="desc">Efficiency rules (3 rules)</span>
│
└── <span class="folder">api/</span>                   <span class="desc">FastAPI routes</span>
    └── <span class="folder">routes/</span>
        ├── <span class="file">upload.py</span>       <span class="desc">POST /api/upload — upload & parse model</span>
        ├── <span class="file">analyze.py</span>      <span class="desc">POST /api/analyze — run analysis</span>
        ├── <span class="file">export.py</span>       <span class="desc">POST /api/export — export results</span>
        └── <span class="file">compare.py</span>      <span class="desc">POST /api/compare — compare models</span></div>

<h2>Key Backend Files</h2>

<div class="file-card">
  <div class="file-card-name">src/main.py</div>
  <div class="file-card-desc">The FastAPI application. Sets up CORS, rate limiting, health check, and registers all API route modules. This is what <code>uvicorn src.main:app</code> runs.</div>
</div>

<div class="file-card">
  <div class="file-card-name">src/store.py</div>
  <div class="file-card-desc">Thread-safe in-memory store. When a model is uploaded and parsed, the graph is stored here with a UUID key. The analyze and export routes look up graphs by this UUID.</div>
</div>

<div class="file-card">
  <div class="file-card-name">src/graph/__init__.py</div>
  <div class="file-card-desc">Defines the core data structures: <strong>LayerNode</strong> (single layer), <strong>Edge</strong> (connection), <strong>Finding</strong> (analysis result), <strong>NeuroScopeGraph</strong> (complete model). All parsers produce this format.</div>
</div>

<!-- ==================== PAGE 3: FRONTEND ==================== -->
<div class="page-break"></div>
<h1>Frontend — frontend/</h1>

<p>The frontend is a <strong>React + TypeScript</strong> application with <strong>Three.js</strong> for 3D rendering. Built with <strong>Vite</strong> for fast development.</p>

<div class="tree"><span class="folder">frontend/</span>
├── <span class="file">package.json</span>           <span class="desc">Dependencies (React, Three.js, Zustand, Axios)</span>
├── <span class="file">vite.config.ts</span>         <span class="desc">Vite build config + API proxy</span>
├── <span class="file">tsconfig.json</span>          <span class="desc">TypeScript configuration</span>
├── <span class="file">index.html</span>             <span class="desc">HTML entry point</span>
│
└── <span class="folder">src/</span>
    ├── <span class="file">main.tsx</span>           <span class="desc">React entry point — mounts App</span>
    ├── <span class="file">App.tsx</span>            <span class="desc">Main layout — upload view or workspace view</span>
    ├── <span class="file">store.ts</span>           <span class="desc">Zustand state (graphData, analysisData, selectedLayer)</span>
    ├── <span class="file">types.ts</span>           <span class="desc">TypeScript interfaces (LayerNode, Edge, GraphData, etc.)</span>
    ├── <span class="file">index.css</span>          <span class="desc">Global styles (dark theme)</span>
    │
    └── <span class="folder">components/</span>
        ├── <span class="file">UploadZone.tsx</span>  <span class="desc">Drag-and-drop file upload with progress bar</span>
        ├── <span class="file">Canvas3D.tsx</span>    <span class="desc">Three.js 3D visualization of the model</span>
        ├── <span class="file">AnalysisPanel.tsx</span> <span class="desc">Shows analysis findings (warnings/errors)</span>
        ├── <span class="file">StatsPanel.tsx</span>  <span class="desc">FLOPs, memory, params overview</span>
        ├── <span class="file">LayerDetail.tsx</span> <span class="desc">Click a layer → see description + code</span>
        └── <span class="file">ExportMenu.tsx</span>  <span class="desc">Export as JSON, TXT, or PNG</span></div>

<h2>Component Flow</h2>

<div class="flow">
  <div class="flow-step">
    <div class="flow-step-label">UploadZone</div>
    <div class="flow-step-desc">File upload</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-label">Store</div>
    <div class="flow-step-desc">Zustand state</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-label">Canvas3D</div>
    <div class="flow-step-desc">3D render</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-label">Panels</div>
    <div class="flow-step-desc">Stats + Analysis</div>
  </div>
</div>

<!-- ==================== PAGE 4: CONFIG ==================== -->
<div class="page-break"></div>
<h1>Configuration — config/</h1>

<div class="tree"><span class="folder">config/</span>
├── <span class="file">analysis_rules.yaml</span>   <span class="desc">All 11 anti-pattern rules with thresholds</span>
├── <span class="file">layer_shapes.yaml</span>     <span class="desc">Layer type → 3D shape mapping</span>
└── <span class="folder">languages/</span>
    └── <span class="file">en.json</span>            <span class="desc">English translations</span></div>

<div class="callout">
  <div class="callout-title">analysis_rules.yaml</div>
  <p>Configures severity levels (CRITICAL/WARNING/INFO), thresholds (e.g., min_depth=15 for skip connections), and enable/disable toggles. Also defines hardware presets for training time estimation (T4, V100, A100, RTX3090, RTX4090).</p>
</div>

<div class="callout">
  <div class="callout-title">layer_shapes.yaml</div>
  <p>Maps each layer category to a 3D geometry: convolution→box, activation→sphere, recurrent→cylinder, attention→octahedron, pooling→small_cube, normalization→slab, etc.</p>
</div>

<!-- ==================== PAGE 5: DOCKER & TESTS ==================== -->
<div class="page-break"></div>
<h1>Docker & Tests</h1>

<h2>docker/</h2>

<div class="tree"><span class="folder">docker/</span>
├── <span class="file">Dockerfile.backend</span>     <span class="desc">Python backend container (FastAPI + ONNX)</span>
└── <span class="file">Dockerfile.frontend</span>    <span class="desc">React frontend container (nginx)</span></div>

<div class="callout">
  <div class="callout-title">docker-compose.yml</div>
  <p>Orchestrates both containers. Backend on port 8000, frontend on port 3000. Includes health checks, resource limits, and volume mounts for data and config.</p>
</div>

<h2>tests/</h2>

<div class="tree"><span class="folder">tests/</span>
├── <span class="folder">test_parsers/</span>
│   └── <span class="file">test_onnx_parser.py</span>    <span class="desc">ONNX parser unit tests</span>
├── <span class="folder">test_analysis/</span>
│   ├── <span class="file">test_flops.py</span>          <span class="desc">FLOPs calculation tests</span>
│   └── <span class="file">test_rules.py</span>          <span class="desc">Analysis rules tests</span>
└── <span class="folder">test_graph/</span>
    └── <span class="file">test_graph.py</span>          <span class="desc">Graph data structure tests</span></div>

<!-- ==================== PAGE 6: DOCS & COMPETITION ==================== -->
<div class="page-break"></div>
<h1>Documentation & Competition</h1>

<h2>docs/</h2>

<div class="tree"><span class="folder">docs/</span>
├── <span class="folder">week1/</span>                 <span class="desc">Week 1 report (HTML + PDF)</span>
├── <span class="folder">week2/</span>                 <span class="desc">Week 2 report (HTML + PDF)</span>
├── <span class="folder">week3/</span>                 <span class="desc">Week 3 report (HTML + PDF)</span>
├── <span class="folder">week4/</span>                 <span class="desc">Week 4 report (HTML + PDF)</span>
└── <span class="folder">specs/</span>                 <span class="desc">Technical specifications</span></div>

<h2>competition/</h2>

<div class="tree"><span class="folder">competition/</span>
├── <span class="file">essay_final.md</span>         <span class="desc">Project introduction essay (800-word limit)</span>
├── <span class="file">team_roster.md</span>         <span class="desc">9 team members with roles</span>
├── <span class="file">submission_checklist.md</span> <span class="desc">AYAIR 2026 submission steps</span>
├── <span class="file">registration.md</span>        <span class="desc">Registration form template</span>
├── <span class="file">timeline.md</span>            <span class="desc">Development timeline</span>
└── <span class="file">*.pdf</span>                  <span class="desc">Generated PDFs (comprehensive + essay)</span></div>

<h2>research/</h2>

<div class="tree"><span class="folder">research/</span>
├── <span class="file">competitor_analysis.md</span> <span class="desc">15 competing tools analyzed</span>
├── <span class="file">african_ml_landscape.md</span> <span class="desc">ML education in Africa</span>
├── <span class="file">ml_anti_patterns.md</span>    <span class="desc">Common deep learning mistakes</span>
└── <span class="file">tech_stack.md</span>          <span class="desc">Technology decisions</span></div>

<!-- ==================== PAGE 7: DATA FLOW ==================== -->
<div class="page-break"></div>
<h1>Complete Data Flow</h1>

<p>Here's exactly what happens when a user uploads a model:</p>

<h2>Step 1: Upload</h2>
<div class="flow">
  <div class="flow-step"><div class="flow-step-label">User</div><div class="flow-step-desc">Drag & drop .onnx file</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">UploadZone</div><div class="flow-step-desc">POST /api/upload</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">upload.py</div><div class="flow-step-desc">Save temp file</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">onnx_parser</div><div class="flow-step-desc">Parse model</div></div>
</div>

<h2>Step 2: Parse</h2>
<div class="flow">
  <div class="flow-step"><div class="flow-step-label">ONNX Model</div><div class="flow-step-desc">GraphProto</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">Extract</div><div class="flow-step-desc">Nodes + edges</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">Shape Inference</div><div class="flow-step-desc">Input/output shapes</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">NeuroScopeGraph</div><div class="flow-step-desc">Unified format</div></div>
</div>

<h2>Step 3: Analyze</h2>
<div class="flow">
  <div class="flow-step"><div class="flow-step-label">AnalysisEngine</div><div class="flow-step-desc">Run rules</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">47+ Rules</div><div class="flow-step-desc">Check patterns</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">Findings</div><div class="flow-step-desc">Warnings + fixes</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">Health Score</div><div class="flow-step-desc">0-100 grade</div></div>
</div>

<h2>Step 4: Visualize</h2>
<div class="flow">
  <div class="flow-step"><div class="flow-step-label">JSON Response</div><div class="flow-step-desc">Graph data</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">Zustand Store</div><div class="flow-step-desc">State update</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">Canvas3D</div><div class="flow-step-desc">Three.js render</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-step"><div class="flow-step-label">User</div><div class="flow-step-desc">Click to inspect</div></div>
</div>

<!-- Footer -->
<div class="footer">
  <span><strong>NeuroScope</strong> — DigiNeurons Team</span>
  <span>AYAIR 2026 · Architecture Guide</span>
</div>

</div>

</body>
</html>"""


def generate_pdf(html_content: str, output_path: str, api_key: str) -> str:
    """Generate PDF using pdf.co API."""
    url = "https://api.pdf.co/v1/pdf/convert/from/html"

    payload = {
        "html": html_content,
        "paperSize": "A4",
        "orientation": "Portrait",
        "printBackground": True,
        "margins": "10mm 10mm 10mm 10mm",
        "name": "NeuroScope_Project_Architecture.pdf"
    }

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    print("[INFO] Sending HTML to pdf.co API...")
    response = requests.post(url, json=payload, headers=headers, timeout=120)

    if response.status_code != 200:
        print(f"[ERROR] HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    result = response.json()

    if result.get("error"):
        print(f"[ERROR] API error: {result}")
        sys.exit(1)

    pdf_url = result["url"]
    print(f"[INFO] Downloading PDF ({result.get('pageCount', '?')} pages, {result.get('credits', '?')} credits)...")

    pdf_response = requests.get(pdf_url, timeout=60)
    if pdf_response.status_code != 200:
        print(f"[ERROR] Download failed: {pdf_response.status_code}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(pdf_response.content)

    print(f"[OK] PDF saved: {output_path}")
    return output_path


def main():
    generate_pdf(HTML_TEMPLATE, OUTPUT_PDF, PDFCO_API_KEY)


if __name__ == "__main__":
    main()
