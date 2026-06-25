# 🧠 NeuroScope

> **AI-Powered 3D Neural Network Architecture Visualizer & Analyzer**
> Upload any ONNX model → See it in 3D → Understand what's wrong → Learn why it matters

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org)
[![Status: In Development](https://img.shields.io/badge/status-in%20development-yellow.svg)](#)

---

## 🎯 What is NeuroScope?

NeuroScope is a web-based tool that helps ML students and developers **understand, visualize, and debug** neural network architectures. Upload an ONNX model file and instantly see it rendered as an interactive 3D scene — with automated analysis that catches common architecture mistakes.

### Current Features (Implemented)

| Feature | Description |
|---------|-------------|
| 🎮 **3D Visualization** | Interactive Three.js rendering of your model architecture with click-to-inspect |
| 🔍 **Architecture Linter** | 11 rules across layer, architecture, and efficiency categories |
| 📊 **FLOPs & Memory** | Per-layer computation cost and memory footprint estimation |
| 📁 **ONNX Support** | Full ONNX model parsing with shape inference and weight extraction |
| 📖 **Educational Content** | Plain-language descriptions of what each layer does and common mistakes |
| 🐳 **Docker Ready** | Docker Compose setup for easy local deployment |

### Roadmap (In Development)

| Feature | Status |
|---------|--------|
| 🔄 **Multi-Format Parsers** | PyTorch (.pt), Keras (.h5), TFLite (.tflite) — building |
| 🆚 **Model Comparison** | Side-by-side architecture diff — building |
| 📤 **Export Suite** | GLB (3D), PDF (reports), Markdown — building |
| 🌍 **Multilingual** | French, Arabic, Swahili, Portuguese — planned |
| 📱 **VS Code Extension** | Real-time 3D visualization in VS Code — planned |
| 🔌 **Offline PWA** | Works without internet after first load — planned |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/neuroscope.git
cd neuroscope

# Start with Docker Compose
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

### Option 2: Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/neuroscope.git
cd neuroscope

# Backend
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## 📁 Project Structure

```
neuroscope/
├── src/                      # Python backend (FastAPI)
│   ├── parsers/              # Model file parsers
│   │   └── onnx_parser.py   # ONNX parser (implemented)
│   ├── analysis/             # Architecture linter & stats
│   │   ├── rules/            # Anti-pattern detection rules (11 rules)
│   │   ├── flops.py          # FLOPs calculator
│   │   └── memory.py         # Memory estimator
│   ├── graph/                # Internal graph representation
│   ├── api/                  # FastAPI routes
│   │   └── routes/           # upload, analyze, export, compare
│   └── main.py               # FastAPI entry point
│
├── frontend/                 # React + Three.js web app
│   └── src/
│       ├── components/       # UI components (UploadZone, Canvas3D, etc.)
│       ├── hooks/            # React hooks
│       └── main.tsx          # Entry point
│
├── config/                   # Configuration files
│   ├── analysis_rules.yaml   # Linter rules & thresholds
│   ├── layer_shapes.yaml     # Layer → 3D shape mapping
│   └── languages/            # i18n (English only currently)
│
├── docker/                   # Dockerfiles
├── docs/                     # Documentation
├── research/                 # Technical research reports
├── tests/                    # Test suite
├── docker-compose.yml        # Docker Compose config
└── requirements.txt          # Python dependencies
```

---

## 🏗️ How It Works

```
Upload ONNX Model (.onnx)
        │
        ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│ ONNX PARSER │────▶│ GRAPH BUILDER│────▶│   ANALYZER    │
│  (Extract   │     │  (Nodes +    │     │  (11 rules:   │
│   layers)   │     │   Edges)     │     │   FLOPs +     │
└─────────────┘     └──────────────┘     │   Memory)     │
                                          └───────┬───────┘
                                                  │
                    ┌─────────────────────────────┼──────────┐
                    ▼                             ▼          ▼
             ┌──────────┐              ┌──────────┐  ┌──────────┐
             │  3D View │              │ Analysis │  │  Stats   │
             │ (Three.js│              │ Panel    │  │ (FLOPs/  │
             └──────────┘              └──────────┘  │  Memory) │
                                                     └──────────┘
```

---

## 🎓 Category: Education Enhancement

NeuroScope is submitted to the **Presidential African Youth in AI and Robotics Competition 2026** under the **Education Enhancement** category.

> *"Initiatives using AI or robotics to inclusively, sustainably and efficiently improve educational offering and learning experiences for students and educators."*

### Why NeuroScope Matters for Africa

- **Free & Open Source** — No cost barrier, MIT License
- **Browser-Based** — No GPU, no installation, works on any device
- **Automated Guidance** — Catches common mistakes where no senior ML engineer is available
- **Educational** — Every layer has a plain-language explanation
- **Deployable** — Docker setup for institutions to run locally

---

## 📅 Development Timeline

| Date | Milestone | Status |
|------|-----------|--------|
| **Jun 2026** | ONNX parser + 3D visualization + analysis engine | ✅ Done |
| **Jul 2026** | PyTorch/Keras parsers + export features | 🚧 In progress |
| **Aug 2026** | Model comparison + advanced analysis | 📋 Planned |
| **Sep 2026** | Polish, deploy, demo video | 📋 Planned |
| **Oct 2026** | Finals (if selected) | 📋 Planned |

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/my-feature`)
3. **Commit** your changes (`git commit -m 'Add my feature'`)
4. **Push** to the branch (`git push origin feature/my-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/neuroscope.git
cd neuroscope

# Backend
pip install -r requirements.txt
pip install pytest httpx  # for testing
pytest

# Frontend
cd frontend
npm install
npm run dev
```

### Areas Where Help is Needed

- Implementing PyTorch/Keras/TFLite parsers
- Adding new analysis rules
- Improving 3D visualization
- Writing educational layer descriptions
- Adding test coverage

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
