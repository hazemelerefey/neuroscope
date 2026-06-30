#!/usr/bin/env python3
"""
NeuroScope Project Introduction Essay — 800 Word Limit
AYAIR 2026 Competition Submission
Updated: Visual Builder concept
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
    <strong>Submitted:</strong> June 2026
  </div>
</div>

<!-- PAGE 1: ESSAY -->
<div class="page">

<h1>Project Introduction</h1>

<p>NeuroScope is an open-source visual deep learning builder that lets students and developers construct complete ML/DL models by dragging, dropping, and selecting components — no coding required. Every action teaches something: users build real, production-ready models while understanding every choice. NeuroScope addresses the critical gap between ML/DL theory and implementation across Africa, where mentorship infrastructure does not exist.</p>

<h2>Origin</h2>

<p>NeuroScope was born from a real problem we encountered as trainees in the <strong>Digilians Initiative</strong> under Egypt's Ministry of Communications and Information Technology (MCIT). During our deep learning training in New Cairo, we watched colleagues struggle with the same challenge: they could write <code>model.fit()</code> and achieve accuracy scores, but could not explain what happened inside their models. The architecture was a black box.</p>

<p>This gap is systemic across Africa. The tools available — Netron (static 2D diagrams), TensorBoard (TensorFlow-locked), and TensorSpace.js (abandoned since 2019) — do not explain what layers do, detect architectural mistakes, or map visualization back to code. None of them teach you how to <em>build</em>. We decided to build the tool we needed ourselves.</p>

<h2>The Problem</h2>

<p>Every year, millions of students across Africa begin learning ML/DL. They attend lectures and study theory, but when they sit down to build their first model, they face a wall. Most students never cross it. The mentorship gap means students are left alone with broken models and no way to understand why they broke. A student in rural Nigeria debugging a failing model at midnight has nowhere to turn.</p>

<h2>Our Solution</h2>

<p>NeuroScope lets users construct complete deep learning models through a visual drag-and-drop interface. The model appears on screen as a <strong>3D machine</strong>: layers are connected blocks, extensions like optimizers and loss functions orbit the core engine with visible cables, and the architecture comes alive as the user builds it. Every action teaches something. Click the optimizer and you see what Adam does differently from SGD. Add a convolutional layer and you understand how filters generate feature maps. When a configuration might cause problems, NeuroScope flags it with a clear explanation and suggested fix.</p>

<p>The tool acts as an <strong>automated mentor</strong>, catching mistakes a senior engineer would catch during code review — available anytime, anywhere, for free. NeuroScope is designed to become the primary tool for building ML/DL models — replacing scattered tutorials, copy-pasted code, and blind debugging with a single, guided environment.</p>

<h2>How It Works</h2>

<p>When building is complete, NeuroScope generates <strong>clean, production-ready code</strong> as a Jupyter notebook or Python file. Take it to Colab, add your dataset, and run. The user understands every line because they chose each piece themselves.</p>

<p>NeuroScope launches as a <strong>web application</strong> with a companion <strong>desktop app</strong> that works both online and offline. Deep learning is the primary focus, with classical ML planned for future releases. The first architecture is a 16-layer CNN with seven configurable extensions: optimizer, activation, loss function, learning rate, batch size, epochs, and data augmentation — each with educational descriptions and consequences. Future versions will support YOLO, ResNet, EfficientNet, and classical models. A <strong>VS Code extension</strong> is planned, allowing users to build and run models directly inside their development environment. For advanced users, a develop mode allows inspecting code, freezing layers, and modifying architectures at a granular level.</p>

<h2>Impact for Africa</h2>

<p>NeuroScope is <strong>free, open-source, and offline-capable</strong>. It supports five languages: English, French, Arabic, Swahili, and Portuguese — covering 2.5 billion speakers. It runs in any browser on any device, including low-end laptops. There is no cost, no subscription, no GPU requirement. Universities can deploy their own instances via Docker.</p>

<p>It aligns with AU STISA 2034, Agenda 2063, and Egypt's MCIT digital transformation strategy. It is <strong>inclusive</strong> — offline, multilingual, any device. It is <strong>sustainable</strong> — open source, community-driven. It is <strong>efficient</strong> — replacing months of trial-and-error with guided, interactive building.</p>

<h2>Sustainability</h2>

<p>Released under the MIT license, NeuroScope is designed for community contribution. Rules, descriptions, and translations are all configurable. The web app and desktop app form the foundation; a VS Code extension will bring the visual builder into the developer's coding environment, enabling construction and execution in the same place.</p>

<div class="quote-block">
  <p>"We built NeuroScope not as a competition entry, but as lasting infrastructure for deep learning education. The problems we faced as trainees are the same problems students face across Africa. NeuroScope does not just show you the machine. It teaches you how to build it."</p>
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
