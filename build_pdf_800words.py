#!/usr/bin/env python3
"""
NeuroScope Project Introduction Essay — 800 Word Limit
AYAIR 2026 Competition Submission
"""

import os
import requests
import sys

PDFCO_API_KEY = os.environ.get("PDFCO_API_KEY", "hazemelerefy@gmail.com_Zjm0ugdruJYHBoDKaykaEpIkye19lcmSG7wGHvZQFFNPY2g9y9xYrxcFT5nUrPBQ")
OUTPUT_PDF = "competition/NeuroScope_Essay_800Words_AYAIR2026.pdf"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NeuroScope — Project Introduction Essay</title>
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

<!-- PAGE 1: ESSAY -->
<div class="page">

<h1>Project Introduction</h1>

<p>NeuroScope is an open-source, AI-powered tool that makes deep learning architectures visible, interactive, and understandable. It transforms how students learn neural networks by providing 3D interactive visualization, real-time code mapping, and automated architecture analysis — addressing a critical gap in deep learning education across Africa and the developing world.</p>

<h2>Origin</h2>

<p>NeuroScope was born from a real problem we encountered as trainees in the <strong>Digilians Initiative</strong> under Egypt's Ministry of Communications and Information Technology (MCIT). During our deep learning training in New Cairo, we watched colleagues struggle with the same challenge: they could write <code>model.fit()</code> and achieve accuracy scores, but could not explain what happened inside their models. The architecture was a black box.</p>

<p>This gap is systemic across Africa. The tools available — Netron (static 2D diagrams), TensorBoard (TensorFlow-locked), and TensorSpace.js (abandoned since 2019) — do not explain what layers do, detect architectural mistakes, or map visualization back to code. We decided to build the tool we needed ourselves.</p>

<h2>The Problem</h2>

<p>Millions of students across Africa begin learning deep learning each year, yet most cannot explain what happens inside the models they build. They copy architectures without understanding skip connections, attention mechanisms, or batch normalization. When models fail, they cannot diagnose the problem. The mentorship gap means students are left alone with broken models and no way to understand why they broke.</p>

<h2>Our Solution</h2>

<p>NeuroScope parses model files (ONNX, PyTorch, Keras, TensorFlow Lite) or Python scripts and generates <strong>interactive 3D visualizations</strong>. Convolutional layers appear as boxes, fully connected layers as planes, attention mechanisms as octahedrons. Clicking any component reveals a plain-language description, the exact code that created it, and parameters/FLOPs/memory footprint.</p>

<p>The built-in analysis engine detects <strong>47+ anti-patterns</strong>: missing activations, sigmoid in deep networks, parameter explosion, and more. Each finding includes severity, explanation, and suggested fix. The visualization updates instantly when code changes — before running it — developing intuition that would otherwise require months of trial and error.</p>

<h2>Deliverables</h2>

<p>NeuroScope is <strong>free and open-source</strong>, designed to work in any environment — including areas with weak or no internet connectivity across Africa.</p>

<div class="deliverable">
  <div class="deliverable-title">1. Web Application (Current Release)</div>
  <div class="deliverable-desc">Browser-based platform for model upload, 3D visualization, analysis, and reporting. No installation required.</div>
</div>

<div class="deliverable">
  <div class="deliverable-title">2. VS Code Extension (Update)</div>
  <div class="deliverable-desc">Real-time code visualization inside VS Code. Architecture renders in a 3D panel, updating live with every edit.</div>
</div>

<div class="deliverable">
  <div class="deliverable-title">3. AI Agent Plugins (Update)</div>
  <div class="deliverable-desc">Integrations for Claude, GitHub Copilot, and other LLM agents. Turns any AI assistant into an architecture-aware code reviewer.</div>
</div>

<div class="deliverable">
  <div class="deliverable-title">4. Desktop Application (Update)</div>
  <div class="deliverable-desc">Standalone application for Windows and Mac. <strong>Downloads and runs locally — completely offline.</strong> Same features as the web version, no internet required.</div>
</div>

<h2>Impact</h2>

<p>NeuroScope is <strong>free, open-source, and offline-capable</strong>. It requires no GPU, no cloud credits, and no installation. It supports five languages: English, French, Arabic, Swahili, and Portuguese — covering 2.5+ billion speakers across Africa and the developing world.</p>

<p>The tool aligns with AU STISA 2034, Agenda 2063, and Egypt's MCIT digital transformation strategy. When no senior ML engineer is available to review a student's architecture, NeuroScope provides that review automatically. A trainee in New Cairo receives the same guidance as a researcher at a leading institution.</p>

<h2>Sustainability</h2>

<p>Released under the MIT license, NeuroScope is designed for community contribution. Analysis rules are YAML-configurable. Layer descriptions are structured data. Translations use JSON language files. Universities can deploy their own instances via Docker.</p>

<div class="quote-block">
  <p>"We built NeuroScope not as a competition entry, but as lasting infrastructure for deep learning education. The problems we faced as trainees are the same problems students face across Africa. NeuroScope turns those shared struggles into shared solutions."</p>
</div>

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
        "name": "NeuroScope_Essay_800Words_AYAIR2026.pdf"
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
