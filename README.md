# 🧠 NeuroScope

> **AI-Powered 3D Neural Network Architecture Visualizer & Analyzer**
> Upload any model → See it in 3D → Understand what's wrong → Export everything

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Status: In Development](https://img.shields.io/badge/status-in%20development-yellow.svg)](#)

---

## 🎯 What is NeuroScope?

NeuroScope is a web-based tool that helps ML students and developers **understand, visualize, and debug** neural network architectures. Unlike existing tools that only show static diagrams, NeuroScope **analyzes your model and tells you what's wrong with it**.

### Key Features

| Feature | Description |
|---------|-------------|
| 🎮 **3D Visualization** | Interactive Three.js rendering of your model architecture |
| 🔍 **Architecture Linter** | 47+ rules that detect common ML anti-patterns |
| 📊 **FLOPs & Memory** | Per-layer computation cost and memory estimation |
| 🔄 **Universal Format** | Supports ONNX, PyTorch (.pt), Keras (.h5), TensorFlow Lite |
| 📤 **Export Suite** | GLB (3D), SVG (diagrams), PDF (reports), Markdown |
| 🆚 **Model Comparison** | Side-by-side architecture diff |
| 🌍 **Multilingual** | English, French, Arabic, Swahili, Portuguese |
| 📱 **Works Anywhere** | Browser-based, no installation, works on mobile |

---

## 🚀 Quick Start

### Option 1: Use the Web App (Coming Soon)
Visit `https://neuroscope.app` (after deployment)

### Option 2: Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/neuroscope.git
cd neuroscope

# Backend
pip install -r requirements.txt
cd backend && uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Option 3: Docker

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
neuroscope/
├── competition/              # Competition submission materials
├── research/                 # Deep research reports (198KB)
├── docs/                     # Documentation & architecture
│
├── src/                      # Python backend (FastAPI)
│   ├── parsers/              # Model file parsers (ONNX, PyTorch, Keras)
│   ├── analysis/             # Architecture linter & stats
│   │   └── rules/            # Anti-pattern detection rules
│   ├── graph/                # Internal graph representation
│   ├── export/               # Export engines (GLB, SVG, PDF, MD)
│   └── utils/                # Shared utilities
│
├── frontend/                 # React + Three.js web app
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── hooks/            # React hooks
│   │   ├── three/            # Three.js 3D rendering
│   │   └── utils/            # Frontend utilities
│   └── public/               # Static assets
│
├── data/                     # Sample models for testing
│   ├── samples/              # Example .onnx, .pt, .h5 files
│   └── fixtures/             # Test data
│
├── config/                   # Configuration files
│   ├── analysis_rules.yaml   # Linter rules & thresholds
│   ├── layer_shapes.yaml     # Layer → 3D shape mapping
│   └── languages/            # i18n translations
│
├── tests/                    # Test suite
├── reports/                  # Generated reports & figures
├── docker/                   # Dockerfiles
└── notebooks/                # Prototyping notebooks
```

---

## 🏗️ How It Works

```
Upload Model (.onnx/.pt/.h5)
        │
        ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   PARSER    │────▶│ GRAPH BUILDER│────▶│   ANALYZER    │
│  (Extract   │     │  (Nodes +    │     │  (47+ rules:  │
│   layers)   │     │   Edges)     │     │   FLOPs +     │
└─────────────┘     └──────────────┘     │   Memory)     │
                                          └───────┬───────┘
                                                  │
                    ┌─────────────────────────────┼──────────┐
                    ▼                             ▼          ▼
             ┌──────────┐              ┌──────────┐  ┌──────────┐
             │  3D View │              │ Analysis │  │  Export  │
             │ (Three.js│              │ Panel    │  │ GLB/SVG/ │
             └──────────┘              └──────────┘  │ PDF/MD   │
                                                     └──────────┘
```

---

## 🎓 Category: Education Enhancement

NeuroScope is submitted to the **Presidential African Youth in AI and Robotics Competition 2026** under the **Education Enhancement** category.

> *"Initiatives using AI or robotics to inclusively, sustainably and efficiently improve educational offering and learning experiences for students and educators."*

### Why NeuroScope Matters for Africa

- **Free & Open Source** — No cost barrier
- **Works Offline** — PWA for low-connectivity areas
- **Browser-Based** — No GPU, no installation, works on phones
- **Multilingual** — French, Arabic, Swahili, Portuguese
- **Bridges the Mentorship Gap** — Automated guidance where no senior ML engineer is available

---

## 📅 Timeline

| Date | Milestone |
|------|-----------|
| **30 Jun 2026** | Competition submission (essay + registration) |
| **Jul 2026** | Core parser + basic 3D visualization |
| **Aug 2026** | Architecture linter + export features |
| **Sep 2026** | Polish, deploy, demo video |
| **Oct 2026** | Finals (if selected) |

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [ONNX](https://onnx.ai/) — Universal model format
- [Three.js](https://threejs.org/) — 3D WebGL rendering
- [FastAPI](https://fastapi.tiangolo.com/) — Backend framework
- [React](https://react.dev/) — Frontend framework

---

<p align="center">
  Made with ❤️ for African ML students and developers
</p>
