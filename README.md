# 🧠 NeuroScope

> **AI-Powered 3D Neural Network Architecture Visualizer & Analyzer**
> Upload any model → See it in 3D → Understand what's wrong → Learn why it matters

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org)
[![Status: In Development](https://img.shields.io/badge/status-in%20development-yellow.svg)](#)

---

## 🎯 What is NeuroScope?

NeuroScope is an **open-source** tool that helps ML students and developers **understand, visualize, and debug** neural network architectures. Upload a model file and instantly see it rendered as an interactive 3D scene — with automated analysis that catches common architecture mistakes.

**Works online and offline.** NeuroScope can be downloaded and run locally, making it accessible to students in areas with weak or no internet connectivity across Africa.

### Core Features

| Feature | Description |
|---------|-------------|
| 🎮 **3D Visualization** | Interactive Three.js rendering of your model architecture with click-to-inspect |
| 🔍 **Architecture Linter** | 47+ anti-pattern detection rules across layer, architecture, and efficiency categories |
| 📊 **FLOPs & Memory** | Per-layer computation cost and memory footprint estimation |
| 📁 **Multi-Format Support** | ONNX, PyTorch, Keras, TensorFlow, TensorFlow Lite |
| 📖 **Educational Content** | Plain-language descriptions of what each layer does and common mistakes |
| 🌍 **Multilingual** | English, French, Arabic, Swahili, Portuguese |
| 🐳 **Docker Ready** | Docker Compose setup for easy local deployment |
| 📥 **Offline Capable** | Desktop application for Windows and Mac — no internet required |

---

## 🚀 Deliverables

NeuroScope is an ecosystem of tools designed to meet students wherever they work:

| # | Deliverable | Status | Description |
|---|-------------|--------|-------------|
| 1 | **Web Application** | ✅ Current Release | Browser-based platform for model upload, 3D visualization, analysis, and reporting |
| 2 | **VS Code Extension** | 🔄 Update | Real-time code visualization inside VS Code — architecture renders in a 3D panel, updating live with every edit |
| 3 | **AI Agent Plugins** | 🔄 Update | Integrations for Claude, GitHub Copilot, and other LLM agents — turns any AI assistant into an architecture-aware code reviewer |
| 4 | **Desktop Application** | 🔄 Update | Standalone app for Windows and Mac — downloads and runs locally, completely offline |

### Roadmap Progression

```
Web Application (Current) → VS Code Extension → AI Agent Plugins → Desktop Application
```

This is a **progression of features**, not a hierarchy. Each update builds on the previous to cover all student needs — from browser-based access to fully offline desktop use.

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/hazemelerefey/neuroscope.git
cd neuroscope

# Start with Docker Compose
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

### Option 2: Run Locally

```bash
# Clone the repo
git clone https://github.com/hazemelerefey/neuroscope.git
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
│   │   ├── rules/            # Anti-pattern detection rules (47+ rules)
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
│   └── languages/            # i18n (EN, FR, AR, SW, PT)
│
├── docker/                   # Dockerfiles
├── docs/                     # Documentation
├── research/                 # Technical research reports
├── competition/              # AYAIR 2026 submission materials
├── tests/                    # Test suite
├── docker-compose.yml        # Docker Compose config
└── requirements.txt          # Python dependencies
```

---

## 🏗️ How It Works

```
Upload Model File (.onnx, .pt, .h5, .tflite)
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
- **Offline Capable** — Desktop application for areas with weak internet
- **Automated Guidance** — Catches common mistakes where no senior ML engineer is available
- **Educational** — Every layer has a plain-language explanation
- **Deployable** — Docker setup for institutions to run locally

### Language Support

| Language | Region | Speakers |
|----------|--------|----------|
| Arabic | Egypt, North Africa, Middle East | 400M+ |
| French | West & Central Africa | 300M+ |
| English | East & Southern Africa, Global | 1.5B+ |
| Swahili | East Africa (Kenya, Tanzania, Rwanda) | 100M+ |
| Portuguese | Lusophone Southern Africa | 250M+ |

---

## 👥 Team: DigiNeurons

| Name | Role | Track |
|------|------|-------|
| **Hazem Khaled** | Team Leader · Deep Learning Engineer | Data Analysis |
| Ahmed Ali | Data Scientist | Data Science |
| Mohamed Abdel Ghani | Data Scientist | Data Science |
| Yossef Shrif | Data Analyst | Data Analysis |
| Yomna Ashraf | Data Analyst | Data Analysis |
| Shahd Khairy | Frontend Developer | Software |
| Mohamed Wagdi | Backend Developer | Software |
| Ziad Mohamed | Backend Developer | Software |
| Yossef Safout | Backend Developer | Software |

---

## 📅 Development Timeline

| Date | Milestone | Status |
|------|-----------|--------|
| **Jun 2026** | ONNX parser + 3D visualization + 47+ analysis rules | ✅ Done |
| **Jul 2026** | PyTorch/Keras parsers + export features | 🚧 In Progress |
| **Aug 2026** | VS Code Extension + AI Agent Plugins | 📋 Planned |
| **Sep 2026** | Desktop Application (Windows/Mac) + polish | 📋 Planned |
| **Oct 2026** | Finals (if selected) | 📋 Planned |

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/my-feature`)
3. **Commit** your changes (`git commit -m 'Add my feature'`)
4. **Push** to the branch (`git push origin feature/my-feature`)
5. **Open** a Pull Request

### Areas Where Help is Needed

- Implementing PyTorch/Keras/TFLite parsers
- Adding new analysis rules
- Improving 3D visualization
- Writing educational layer descriptions
- Adding translations for new languages
- Desktop application development (Electron)

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
