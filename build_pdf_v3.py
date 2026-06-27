#!/usr/bin/env python3
"""
NeuroScope Project Introduction PDF — v3 Final
Professional minimalistic design with corrected deliverables.
"""

import os
import requests
import sys

PDFCO_API_KEY = os.environ.get("PDFCO_API_KEY", "hazemelerefy@gmail.com_Zjm0ugdruJYHBoDKaykaEpIkye19lcmSG7wGHvZQFFNPY2g9y9xYrxcFT5nUrPBQ")
OUTPUT_PDF = "competition/NeuroScope_Project_Introduction_AYAIR2026.pdf"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NeuroScope — Project Introduction</title>
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

  .team-table .track {
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #6c6c8a;
  }

  /* Info Grid */
  .info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 24px 0;
  }

  .info-box {
    padding: 16px;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    text-align: center;
  }

  .info-box-label {
    font-size: 7.5pt;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 4px;
  }

  .info-box-value {
    font-size: 13pt;
    font-weight: 700;
    color: #1a1a2e;
  }

  /* Deliverables */
  .deliverable {
    padding: 16px 20px;
    border-left: 3px solid #1a1a2e;
    margin: 16px 0;
    background: #fafafa;
  }

  .deliverable-title {
    font-size: 11pt;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 4px;
  }

  .deliverable-desc {
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
  <div class="cover-subtitle">AI-Powered 3D Neural Network Architecture Visualizer & Analyzer</div>
  <div class="cover-line"></div>
  <div class="cover-meta">
    <strong>Team:</strong> DigiNeurons<br>
    <strong>Category:</strong> Education Enhancement<br>
    <strong>Submitted:</strong> June 2026
  </div>
</div>

<!-- PAGE 1: TEAM -->
<div class="page">

<h1>Team</h1>

<table class="team-table">
  <thead>
    <tr>
      <th>Name</th>
      <th>Role</th>
      <th>Track</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Hazem Khaled</strong></td>
      <td>Team Leader · Deep Learning Engineer</td>
      <td class="track">Data Analysis</td>
    </tr>
    <tr>
      <td>Ahmed Ali</td>
      <td>Data Scientist</td>
      <td class="track">Data Science</td>
    </tr>
    <tr>
      <td>Mohamed Abdel Ghani</td>
      <td>Data Scientist</td>
      <td class="track">Data Science</td>
    </tr>
    <tr>
      <td>Yossef Shrif</td>
      <td>Data Analyst</td>
      <td class="track">Data Analysis</td>
    </tr>
    <tr>
      <td>Yomna Ashraf</td>
      <td>Data Analyst</td>
      <td class="track">Data Analysis</td>
    </tr>
    <tr>
      <td>Shahd Khairy</td>
      <td>Frontend Developer</td>
      <td class="track">Software</td>
    </tr>
    <tr>
      <td>Mohamed Wagdi</td>
      <td>Backend Developer</td>
      <td class="track">Software</td>
    </tr>
    <tr>
      <td>Ziad Mohamed</td>
      <td>Backend Developer</td>
      <td class="track">Software</td>
    </tr>
    <tr>
      <td>Yossef Safout</td>
      <td>Backend Developer</td>
      <td class="track">Software</td>
    </tr>
  </tbody>
</table>

<div class="info-grid">
  <div class="info-box">
    <div class="info-box-label">Data Analysis</div>
    <div class="info-box-value">3</div>
  </div>
  <div class="info-box">
    <div class="info-box-label">Data Science</div>
    <div class="info-box-value">2</div>
  </div>
  <div class="info-box">
    <div class="info-box-label">Software</div>
    <div class="info-box-value">4</div>
  </div>
</div>

<!-- PAGE 2: ORIGIN -->
<div class="page-break"></div>
<h1>Origin</h1>

<p>NeuroScope was born from a real problem we encountered firsthand. As trainees in the <strong>Digilians Initiative</strong> under Egypt's Ministry of Communications and Information Technology (MCIT), we studied deep learning and machine learning as part of our professional development program in New Cairo.</p>

<p>During our training, we watched our colleagues struggle with the same challenge: they could write <code>model.fit()</code> and achieve accuracy scores, but when asked to explain what happened inside the model — why a skip connection exists, what a batch normalization layer does, or why the network stops learning — they could not answer. The architecture was a black box. They could operate it, but they could not see inside it.</p>

<p>This gap is not unique to our cohort. It is a systemic problem across Africa and the developing world. Egypt's MCIT, the African Union's Agenda 2063, and STISA 2034 all call for technically skilled youth to lead digital industrialization. But the tools available to these students were not designed for them.</p>

<h2>Why Existing Tools Fall Short</h2>

<ul>
  <li><strong>Netron</strong> shows static 2D diagrams — students see shapes but learn nothing about function.</li>
  <li><strong>TensorBoard</strong> is locked to TensorFlow and requires running training before visualization.</li>
  <li><strong>TensorSpace.js</strong> offered 3D visualization but has been abandoned since 2019.</li>
  <li><strong>No tool</strong> detects architectural mistakes, explains what layers do, or maps visualization back to code.</li>
</ul>

<div class="quote-block">
  <p>"We thought: if no one has built the tool we need, we will build it ourselves."</p>
</div>

<p>NeuroScope is our answer — a tool that covers every issue we faced while studying deep learning, turned into features that make the subject easier to learn, understand, and apply.</p>

<!-- PAGE 3: THE PROBLEM -->
<div class="page-break"></div>
<h1>The Problem</h1>

<p>Millions of students across Africa begin their journey into deep learning each year. They enroll in courses, attend programs, and learn to train models. But beneath this surface lies a fundamental gap: <strong>most students do not understand what happens inside the models they build.</strong></p>

<p>They copy architectures from GitHub without knowing why a ResNet uses skip connections, or why a transformer uses multi-head attention, or why batch normalization stabilizes training. When their model fails, they cannot diagnose the problem. The architecture is a black box — they can operate it, but they cannot see inside it.</p>

<p>This gap is especially harmful in developing regions. The mentorship gap means that when no senior ML engineer is available to review a student's architecture, the student is left alone with a broken model and no way to understand why it broke.</p>

<!-- PAGE 4: OUR SOLUTION -->
<div class="page-break"></div>
<h1>Our Solution</h1>

<p>NeuroScope is an open-source tool that transforms how students learn deep learning by making neural network architectures <strong>visible, interactive, and understandable.</strong></p>

<h2>Core Capabilities</h2>

<p>A student uploads a model file — ONNX, PyTorch, Keras, or TensorFlow Lite — or opens a Python script. NeuroScope parses the code and generates an <strong>interactive 3D visualization</strong> of the architecture. Convolutional layers appear as boxes, fully connected layers as planes, recurrent layers as cylinders, and attention mechanisms as octahedrons.</p>

<p>Clicking any component reveals three things: a plain-language description of what the layer does, the exact code that created it, and the layer's parameters, FLOPs, and memory footprint. This bidirectional mapping — from visualization to code and back — is the core of NeuroScope's educational value.</p>

<h2>Architecture Health Check</h2>

<p>The built-in analysis engine detects <strong>47+ common anti-patterns</strong>: missing activation functions, sigmoid in deep networks, missing skip connections, parameter explosion, redundant layers, and more. Each finding includes severity, explanation, and a suggested fix — functioning as a spell-checker for neural network design. Students receive instant architectural feedback without needing a senior engineer to review their work.</p>

<h2>Real-Time Code Visualization</h2>

<p>NeuroScope updates the 3D visualization instantly when a student edits code — before running it. Changing the number of filters, adjusting dropout, or adding a layer immediately shows the architectural impact, developing intuition that would otherwise require months of trial and error.</p>

<!-- PAGE 5: DELIVERABLES -->
<div class="page-break"></div>
<h1>Deliverables</h1>

<p>NeuroScope is not a single product — it is an ecosystem of tools designed to meet students and developers wherever they work.</p>

<div class="deliverable">
  <div class="deliverable-title">1. Web Application (Current Release)</div>
  <div class="deliverable-desc">A browser-based platform for uploading models, viewing 3D visualizations, running architecture analysis, and generating reports. No installation required. Works on any device with a modern browser. <strong>Always free and open-source.</strong></div>
</div>

<div class="deliverable">
  <div class="deliverable-title">2. VS Code Extension (Update)</div>
  <div class="deliverable-desc">Real-time code visualization directly inside VS Code. As students write Python code, the extension parses it and renders the architecture in a 3D panel — updating live with every edit. Includes inline anti-pattern warnings, code-to-architecture mapping, and one-click export.</div>
</div>

<div class="deliverable">
  <div class="deliverable-title">3. AI Agent Plugins (Update)</div>
  <div class="deliverable-desc">Integrations for AI coding assistants including Claude, GitHub Copilot, and other LLM-based agents. When a student asks an AI agent to review or explain their model code, the plugin provides architectural context — layer descriptions, anti-pattern detection, and visualization data — enabling more informed and accurate assistance.</div>
</div>

<div class="deliverable">
  <div class="deliverable-title">4. Desktop Application (Update)</div>
  <div class="deliverable-desc">A standalone application for Windows and Mac that can be downloaded and run locally. <strong>Works completely offline</strong> — critical for students in areas with weak or no internet connectivity. Same features as the web version, but without requiring a browser or internet connection.</div>
</div>

<h2>Technical Stack</h2>

<ul>
  <li><strong>Backend:</strong> Python, FastAPI, ONNX Runtime</li>
  <li><strong>Frontend:</strong> React, Three.js, TypeScript</li>
  <li><strong>Extension:</strong> VS Code Extension API, Webview panels</li>
  <li><strong>Plugins:</strong> LLM function calling, MCP protocol support</li>
  <li><strong>Desktop:</strong> Electron (Windows/Mac), offline-capable</li>
  <li><strong>Deployment:</strong> Docker, Progressive Web App</li>
</ul>

<!-- PAGE 6: IMPACT -->
<div class="page-break"></div>
<h1>Impact</h1>

<p>NeuroScope is <strong>free, open-source, and designed for the environments where it is needed most.</strong> It works entirely in the browser with no installation. It functions as a progressive web application that works offline — critical for areas with intermittent connectivity. It requires no GPU, no cloud credits, and no expensive licenses.</p>

<h2>Language Support</h2>

<p>NeuroScope supports five languages: <strong>English, French, Arabic, Swahili, and Portuguese</strong> — covering Egypt's Arabic-speaking regions, Francophone West and Central Africa, East Africa's Swahili-speaking regions, and Lusophone Southern Africa.</p>

<h2>Alignment with Development Goals</h2>

<ul>
  <li><strong>AU STISA 2034</strong> — Building scientific literacy across the continent</li>
  <li><strong>Agenda 2063</strong> — Inclusive development and technical capacity building</li>
  <li><strong>Egypt MCIT Digital Transformation</strong> — National priority for technical education</li>
  <li><strong>Digilians Initiative</strong> — Direct response to real training needs</li>
</ul>

<p>The mentorship gap is real: when no senior ML engineer is available to review a student's architecture, NeuroScope provides that review automatically. A trainee in New Cairo can receive the same architectural guidance as a researcher at a leading institution.</p>

<!-- PAGE 7: SUSTAINABILITY -->
<div class="page-break"></div>
<h1>Sustainability</h1>

<p>NeuroScope is released under the <strong>MIT license</strong> as a fully open-source project. The architecture is designed for community contribution:</p>

<ul>
  <li><strong>Analysis rules</strong> are defined in YAML configuration files — educators and researchers can add new anti-patterns without modifying code.</li>
  <li><strong>Layer descriptions</strong> are stored as structured data — the community can contribute educational content in any language.</li>
  <li><strong>Translations</strong> are managed through JSON language files — adding a new language requires no code changes.</li>
  <li><strong>Institutional deployment</strong> — universities and training programs can run their own instances using Docker.</li>
</ul>

<p>We are building NeuroScope not as a competition entry, but as <strong>lasting infrastructure for deep learning education.</strong> Every student who struggles to understand why their network is not learning, or what each block in a transformer does, will benefit from this tool.</p>

<p>The problems we faced as trainees are the same problems students face across Africa and the developing world. NeuroScope turns those shared struggles into shared solutions.</p>

<!-- Footer -->
<div class="footer">
  <span><strong>NeuroScope</strong> — DigiNeurons Team</span>
  <span>AYAIR 2026 · Education Enhancement</span>
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
        "name": "NeuroScope_Project_Introduction_AYAIR2026.pdf"
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
