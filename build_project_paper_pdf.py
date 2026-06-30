#!/usr/bin/env python3
"""
NeuroScope Project Paper — AYAIR 2026
Sent via email after Jotform submission
"""

import os
import requests
import sys

PDFCO_API_KEY = os.environ.get("PDFCO_API_KEY", "hazemelerefy@gmail.com_Zjm0ugdruJYHBoDKaykaEpIkye19lcmSG7wGHvZQFFNPY2g9y9xYrxcFT5nUrPBQ")
OUTPUT_PDF = "competition/NeuroScope_Project_Paper_AYAIR2026.pdf"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NeuroScope — Project Paper</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1a1a2e;
    line-height: 1.75;
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

  /* Team Table */
  .team-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 9.5pt;
  }

  .team-table th {
    background: #1a1a2e;
    color: #fff;
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 10px 14px;
    text-align: left;
  }

  .team-table td {
    padding: 10px 14px;
    border-bottom: 1px solid #eee;
  }

  .team-table tr:last-child td { border-bottom: none; }
  .team-table tr:nth-child(even) { background: #fafafa; }

  .team-table .leader {
    font-weight: 600;
    color: #1a1a2e;
  }

  /* Feature Cards */
  .feature {
    padding: 16px 20px;
    border-left: 3px solid #1a1a2e;
    margin: 16px 0;
    background: #fafafa;
  }

  .feature-title {
    font-size: 11pt;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 4px;
  }

  .feature-desc {
    font-size: 9.5pt;
    color: #6c6c8a;
    margin: 0;
  }

  /* Quote */
  .quote-block {
    padding: 20px 24px;
    margin: 24px 0;
    border-left: 3px solid #1a1a2e;
    background: #fafafa;
  }

  .quote-block p {
    font-size: 10.5pt;
    font-style: italic;
    color: #444;
    margin: 0;
  }

  /* Stats */
  .stats {
    display: flex;
    gap: 16px;
    margin: 20px 0;
  }

  .stat {
    flex: 1;
    padding: 16px;
    background: #fafafa;
    border: 1px solid #eee;
    text-align: center;
  }

  .stat-number {
    font-size: 20pt;
    font-weight: 700;
    color: #1a1a2e;
  }

  .stat-label {
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #6c6c8a;
    margin-top: 4px;
  }

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
  ul { margin: 12px 0 12px 20px; }
  li { margin-bottom: 6px; font-size: 10pt; }

  @media print {
    body { font-size: 10pt; }
    .cover { page-break-after: always; }
    h1 { page-break-after: avoid; }
    .team-table { page-break-inside: avoid; }
  }
</style>
</head>
<body>

<!-- COVER -->
<div class="cover">
  <div class="cover-label">AYAIR 2026 — Third Edition</div>
  <div class="cover-title">NeuroScope</div>
  <div class="cover-subtitle">Visual Deep Learning Builder — Learn by Building, Not by Reading</div>
  <div class="cover-line"></div>
  <div class="cover-meta">
    <strong>Team:</strong> DigiNeurons<br>
    <strong>Category:</strong> Education Enhancement<br>
    <strong>Nature:</strong> Group Project (8 Members)<br>
    <strong>Submitted:</strong> June 2026
  </div>
</div>

<!-- PAGE 1: ESSAY + TEAM -->
<div class="page">

<h1>Project Introduction</h1>

<p>NeuroScope is an open-source visual deep learning builder that lets students and developers construct complete ML/DL models by dragging, dropping, and selecting components — no coding required. It transforms the way deep learning is taught by making every action educational: users build real, production-ready models while understanding every choice they make. NeuroScope addresses the critical gap between ML/DL theory and implementation across Africa, where the mentorship infrastructure that could bridge this gap simply does not exist.</p>

<h2>Origin</h2>

<p>NeuroScope was born from a real problem we encountered as trainees in the <strong>Digilians Initiative</strong> under Egypt's Ministry of Communications and Information Technology (MCIT). During our deep learning training in New Cairo, we watched colleagues struggle with the same challenge: they could write <code>model.fit()</code> and achieve accuracy scores, but could not explain what happened inside their models. The architecture was a black box. They copied architectures from GitHub without understanding why each layer existed. When training failed, they had no way to diagnose the problem.</p>

<p>This gap is systemic across Africa. The tools available — Netron (static 2D diagrams), TensorBoard (TensorFlow-locked), and TensorSpace.js (abandoned since 2019) — do not explain what layers do, detect architectural mistakes, or map visualization back to code. None of them teach you how to <em>build</em>. They show you the machine after it is built. They do not teach you how to build it. We decided to build the tool we needed ourselves.</p>

<h1>Team — DigiNeurons</h1>

<p>This is a <strong>group project</strong> submitted by the team leader on behalf of all eight members. The team is organized into three tracks: Data Analysis, Data Science, and Software Development.</p>

<table class="team-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Name</th>
      <th>Role</th>
      <th>Track</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td class="leader">Hazem Khaled</td>
      <td>Team Leader · Data Analyst</td>
      <td>Data Analysis</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Yomna Ashraf</td>
      <td>Data Analyst</td>
      <td>Data Analysis</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Yossef Shrif</td>
      <td>Data Analyst</td>
      <td>Data Analysis</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Shahd Khairy</td>
      <td>Frontend Developer</td>
      <td>Software</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Mohamed Wagdi</td>
      <td>Backend Developer</td>
      <td>Software</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Ziad Mohamed</td>
      <td>Backend Developer</td>
      <td>Software</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Yossef Safout</td>
      <td>Backend Developer</td>
      <td>Software</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Mohamed Abdel Ghani</td>
      <td>Data Scientist</td>
      <td>Data Science</td>
    </tr>
  </tbody>
</table>

<h1>Problem Statement</h1>

<p>Every year, millions of students across Africa begin learning machine learning and deep learning. They attend lectures, study theory, and watch tutorials. But when they sit down to build their first model, they face a wall. The gap between understanding what a convolutional layer is and actually writing one in code is enormous. Most students never cross it. They copy architectures from GitHub without understanding why each layer exists, run <code>model.fit()</code> without knowing what happens inside, and when training fails, they cannot diagnose the problem.</p>

<p>This is not a talent problem. It is an infrastructure problem. Across Africa, there are not enough senior ML engineers to guide every student. A student in rural Nigeria debugging a failing model at midnight has nowhere to turn. The mentorship gap means students are left alone with broken models and no way to understand why they broke.</p>

<h1>Solution Overview</h1>

<p>NeuroScope lets users construct complete deep learning models through a visual drag-and-drop interface. The model appears on screen as a <strong>3D machine</strong>: layers are connected blocks, extensions like optimizers and loss functions orbit the core engine with visible cables, and the entire architecture comes alive as the user builds it.</p>

<p>Every action teaches something. Click the optimizer extension and you see what Adam does differently from SGD. Add a convolutional layer and you understand how filters slide across your input and generate feature maps. When a configuration might cause problems — such as using sigmoid in a deep network or a learning rate that is too high — NeuroScope flags it with a clear explanation and suggested fix.</p>

<p>The tool acts as an <strong>automated mentor</strong>, catching mistakes that a senior engineer would catch during code review — available anytime, anywhere, for free.</p>

<h1>Key Features</h1>

<div class="feature">
  <div class="feature-title">Visual Drag-and-Drop Builder</div>
  <div class="feature-desc">Construct complete ML/DL models by selecting and connecting components — no coding required. The 3D visualization makes architecture tangible and intuitive.</div>
</div>

<div class="feature">
  <div class="feature-title">Learn While Building</div>
  <div class="feature-desc">Every option includes plain-language explanations, recommended use cases, and consequences of each choice. Students learn by doing, not by reading documentation.</div>
</div>

<div class="feature">
  <div class="feature-title">Production-Ready Code Export</div>
  <div class="feature-desc">Export clean Jupyter notebooks or Python files. Take to Google Colab, add your dataset, and run. The code follows best practices because every choice was guided.</div>
</div>

<div class="feature">
  <div class="feature-title">Automated Architecture Review</div>
  <div class="feature-desc">Real-time detection of common mistakes and anti-patterns with severity ratings, explanations, and suggested fixes — like a senior engineer reviewing your code.</div>
</div>

<div class="feature">
  <div class="feature-title">Develop Mode for Advanced Users</div>
  <div class="feature-desc">Inspect full model code, freeze or unfreeze individual layers, modify architectures at a granular level, and customize the head layer for specific classification tasks.</div>
</div>

<div class="feature">
  <div class="feature-title">Multi-Model Support</div>
  <div class="feature-desc">Launches with CNN (deep learning). Future releases will support YOLO, ResNet, EfficientNet, and classical ML models — making NeuroScope a comprehensive builder for the entire ML/DL spectrum.</div>
</div>

<h1>Technical Architecture</h1>

<h2>Product Platform</h2>

<p>NeuroScope launches as a <strong>web application</strong> (primary product) with a companion <strong>desktop application</strong> that works both online and offline — ensuring access in any environment, from university labs to areas with no connectivity. A <strong>VS Code extension</strong> is planned for future release, allowing users to build and run models directly inside their development environment.</p>

<h2>Technology Stack</h2>

<div class="feature">
  <div class="feature-title">Frontend</div>
  <div class="feature-desc">React 18 + TypeScript + Three.js (React Three Fiber) for 3D rendering + Zustand for state management + Tailwind CSS for styling</div>
</div>

<div class="feature">
  <div class="feature-title">Backend</div>
  <div class="feature-desc">Python + FastAPI for API services + model parsers (ONNX, PyTorch, Keras, TensorFlow Lite) + analysis engine with 47+ rules</div>
</div>

<div class="feature">
  <div class="feature-title">Infrastructure</div>
  <div class="feature-desc">Docker containerization + CI/CD pipeline + progressive web app (PWA) for offline capability</div>
</div>

<h2>First Supported Model: CNN v16</h2>

<p>A 16-layer convolutional neural network with <strong>seven configurable extensions</strong>:</p>

<table class="team-table">
  <thead>
    <tr>
      <th>Extension</th>
      <th>Category</th>
      <th>Options</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Optimizer</td><td>Training</td><td>SGD, Adam, AdamW, RMSprop</td></tr>
    <tr><td>Activation</td><td>Training</td><td>ReLU, LeakyReLU, SiLU, Mish, GELU</td></tr>
    <tr><td>Loss Function</td><td>Training</td><td>CrossEntropy, FocalLoss, LabelSmoothing</td></tr>
    <tr><td>Learning Rate</td><td>Training</td><td>0.1, 0.01, 0.001, 0.0001</td></tr>
    <tr><td>Batch Size</td><td>Functional</td><td>8, 16, 32, 64, 128</td></tr>
    <tr><td>Epochs</td><td>Functional</td><td>50, 100, 200, 500</td></tr>
    <tr><td>Augmentation</td><td>Data</td><td>None, Basic, Advanced, Custom</td></tr>
  </tbody>
</table>

<p>Each option includes educational content: what it is, when to use it, what happens if misconfigured, and the code it generates.</p>

<h1>Impact & Alignment</h1>

<div class="stats">
  <div class="stat">
    <div class="stat-number">5</div>
    <div class="stat-label">Languages</div>
  </div>
  <div class="stat">
    <div class="stat-number">0</div>
    <div class="stat-label">Cost</div>
  </div>
  <div class="stat">
    <div class="stat-number">2.5B+</div>
    <div class="stat-label">Speakers Reached</div>
  </div>
</div>

<p>NeuroScope is <strong>free, open-source, and offline-capable</strong>. It supports English, French, Arabic, Swahili, and Portuguese. It runs in any browser on any device, including low-end laptops and tablets. There is no cost, no subscription, no GPU requirement. Universities can deploy their own instances via Docker.</p>

<p>The tool aligns with <strong>AU STISA 2034</strong>, <strong>Agenda 2063</strong>, and <strong>Egypt's MCIT digital transformation strategy</strong>. It is inclusive because it works offline, in multiple languages, on any device. It is sustainable because it is open source and community-driven. It is efficient because it replaces months of trial-and-error learning with guided, interactive model building.</p>

<h1>Sustainability</h1>

<p>Released under the <strong>MIT license</strong>, NeuroScope is designed for community contribution. Analysis rules are YAML-configurable. Layer descriptions are structured data. Translations use JSON language files. New model architectures can be added through structured definitions. The web app and desktop app form the foundation; a VS Code extension will bring the visual builder directly into the developer's coding environment.</p>

<div class="quote-block">
  <p>"We built NeuroScope not as a competition entry, but as lasting infrastructure for deep learning education. The problems we faced as trainees are the same problems students face across Africa. NeuroScope does not just show you the machine. It teaches you how to build it."</p>
</div>

<!-- Footer -->
<div class="footer">
  <span><strong>NeuroScope</strong> — DigiNeurons Team</span>
  <span>AYAIR 2026 · Education Enhancement · Group Project</span>
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
        "name": "NeuroScope_Project_Paper_AYAIR2026.pdf"
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

    with open(output_path, "wb") as f:
        f.write(pdf_response.content)

    print(f"[OK] PDF saved: {output_path}")
    return output_path


def main():
    generate_pdf(HTML_TEMPLATE, OUTPUT_PDF, PDFCO_API_KEY)


if __name__ == "__main__":
    main()
