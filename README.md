<p align="center">
  <img src="https://img.shields.io/badge/🧠-NeuroScope-1a1a2e?style=for-the-badge&labelColor=1a1a2e&color=6c6c8a" alt="NeuroScope">
</p>

<h1 align="center">NeuroScope</h1>

<p align="center">
  <strong>Visual Deep Learning Builder</strong><br>
  Build ML/DL models by dragging, dropping, and connecting — no coding required.<br>
  Every action teaches something. Export a clean notebook. Run it anywhere.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/status-in%20development-yellow.svg" alt="In Development">
  <img src="https://img.shields.io/badge/offline-capable-brightgreen.svg" alt="Offline Capable">
  <img src="https://img.shields.io/badge/languages-5-blue.svg" alt="5 Languages">
</p>

---

## What is NeuroScope?

NeuroScope is an **open-source visual builder** for deep learning and machine learning models. Instead of writing code line by line, you **drag components onto a canvas, connect them, and configure options through guided panels** — while the tool explains what every choice does and why it matters.

The model appears on screen as a **3D machine**: layers are connected blocks, extensions like optimizers and loss functions orbit the core engine with visible cables. When you're done, you export a **clean, production-ready Jupyter notebook** or Python file — code you understand because you chose every piece.

> NeuroScope doesn't run your code. It **builds** your code. You take it to Colab, add your dataset, and run.

---

## The Problem We Solve

Every year, millions of students across Africa begin learning ML/DL. They attend lectures, study theory, and watch tutorials. But when they sit down to build their first model, they face a wall. The gap between understanding what a convolutional layer is and actually writing one is enormous. Most students never cross it.

Existing tools don't help. Netron shows static diagrams. TensorBoard monitors training. Neither teaches you how to **build**. They show you the machine after it's built. They don't teach you how to build it.

**NeuroScope is the tool we needed — so we built it.**

---

## Core Features

| Feature | Description |
|---------|-------------|
| 🎮 **Drag & Drop Builder** | Assemble models visually by placing and connecting components on a canvas |
| 🏗️ **3D Machine View** | Your model appears as a 3D machine — layers are blocks, extensions orbit with cables |
| 📖 **Learn As You Build** | Every option includes plain-language explanations, when to use it, and what happens if misconfigured |
| 📓 **Notebook Export** | Output a ready-to-run `.ipynb` or `.py` — clean, annotated, production-ready code |
| 🧩 **7 Extensions** | Optimizer, Activation, Loss, Learning Rate, Batch Size, Epochs, Augmentation |
| 🔧 **Develop Mode** | Inspect code, freeze/unfreeze layers, modify architectures at a granular level |
| 🌐 **Web + Desktop** | Browser-based web app + desktop app (online/offline) |
| 🌍 **5 Languages** | English, French, Arabic, Swahili, Portuguese |

---

## First Model: CNN v16

The launch model is a 16-layer Convolutional Neural Network with **7 configurable extensions**:

| Extension | Options | What It Does |
|-----------|---------|--------------|
| ⚡ **Optimizer** | SGD, Adam, AdamW, RMSprop | How the model updates its weights |
| 🔥 **Activation** | ReLU, LeakyReLU, SiLU, Mish, GELU | Adds non-linearity for complex pattern learning |
| 💚 **Loss Function** | CrossEntropy, FocalLoss, LabelSmoothing | Measures prediction error |
| 📈 **Learning Rate** | 0.1, 0.01, 0.001, 0.0001 | Step size for weight updates |
| 📦 **Batch Size** | 8, 16, 32, 64, 128 | Samples per training step |
| 🔄 **Epochs** | 50, 100, 200, 500 | Full dataset passes |
| 🟣 **Augmentation** | None, Basic, Advanced, Custom | Data expansion strategies |

Each option includes educational content: what it is, when to use it, consequences of misconfiguration, and the code it generates.

### Roadmap

| Model | Type | Status |
|-------|------|--------|
| CNN v16 | Image Classification | ✅ Current |
| YOLO | Object Detection | 📋 Planned |
| ResNet | Image Classification | 📋 Planned |
| EfficientNet | Efficient Classification | 📋 Planned |
| Classical ML | SVM, Random Forest, XGBoost | 📋 Planned |

---

## Product Platform

| Platform | Status | Description |
|----------|--------|-------------|
| **Web Application** | ✅ Current | Browser-based visual builder — no installation required |
| **Desktop Application** | 🔄 In Progress | Windows + Mac — works online and offline |
| **VS Code Extension** | 📋 Planned | Build and run models directly inside VS Code |

---

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/hazemelerefey/neuroscope.git
cd neuroscope
docker-compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

### Local Development

```bash
# Backend
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models` | GET | List available model families |
| `/api/models/{family}/{version}` | GET | Full model definition (layers, extensions, options) |
| `/api/export/notebook` | POST | Generate Jupyter notebook from visual config |
| `/api/export/yaml` | POST | Generate model YAML from visual config |
| `/api/educational/{topic}` | GET | Educational content for DL topics |

---

## Project Structure

```
neuroscope/
├── src/                          # Python backend (FastAPI)
│   ├── data/models/              # Model definitions (CNN v16 JSON)
│   ├── api/routes/               # API endpoints
│   │   ├── models.py             # Model family/version definitions
│   │   ├── export.py             # Notebook & YAML generation
│   │   └── educational.py        # DL educational content
│   └── main.py                   # FastAPI entry point
│
├── frontend/                     # React + Three.js web app
│   └── src/
│       ├── components/           # UI components
│       │   ├── Canvas3D.tsx      # 3D machine visualization
│       │   ├── ModelSelector.tsx # Model family/version/size picker
│       │   ├── ExtensionConfig.tsx # Extension option panels
│       │   ├── NotebookWindow.tsx  # Live code preview
│       │   ├── DevelopMode.tsx   # Layer inspector
│       │   └── InfoPanel.tsx     # Model summary panel
│       ├── store.ts              # Zustand state management
│       └── types.ts              # TypeScript type definitions
│
├── config/                       # Configuration
│   ├── builder_rules.yaml        # Validation rules (warn on common mistakes)
│   ├── layer_shapes.yaml         # Layer → 3D shape mapping
│   └── languages/                # i18n (EN, FR, AR, SW, PT)
│
├── docs/                         # Documentation
│   ├── brd/                      # Business Requirements Document
│   ├── prd/                      # Product Requirements Document
│   └── technical/                # Technical Architecture + Frontend Guide
│
├── competition/                  # AYAIR 2026 submission materials
├── tests/                        # Test suite
├── docker-compose.yml            # Docker config
└── requirements.txt              # Python dependencies
```

---

## AYAIR 2026 — Education Enhancement

NeuroScope is submitted to the **Presidential African Youth in AI and Robotics Competition 2026** under the **Education Enhancement** category.

> *"Initiatives using AI or robotics to inclusively, sustainably and efficiently improve educational offering and learning experiences for students and educators."*

### Why It Matters for Africa

- **Free & Open Source** — MIT License, no cost barrier
- **No Coding Required** — visual builder lowers the entry barrier
- **Learn By Doing** — every component teaches what it does
- **Offline Capable** — desktop app works without internet
- **Clean Output** — exported notebooks teach proper code structure
- **Deployable** — Docker setup for universities

### Language Support

| Language | Region | Speakers |
|----------|--------|----------|
| 🇪🇬 Arabic | Egypt, North Africa, Middle East | 400M+ |
| 🇫🇷 French | West & Central Africa | 300M+ |
| 🇬🇧 English | East & Southern Africa, Global | 1.5B+ |
| 🇰🇪 Swahili | East Africa (Kenya, Tanzania, Rwanda) | 100M+ |
| 🇵🇹 Portuguese | Lusophone Southern Africa | 250M+ |

---

## Team — DigiNeurons

| # | Name | Role | Track |
|---|------|------|-------|
| 1 | **Hazem Khaled** | Team Leader · Data Analyst | Data Analysis |
| 2 | Yomna Ashraf | Data Analyst | Data Analysis |
| 3 | Yossef Shrif | Data Analyst | Data Analysis |
| 4 | Shahd Khairy | Frontend Developer | Software |
| 5 | Mohamed Wagdi | Backend Developer | Software |
| 6 | Ziad Mohamed | Backend Developer | Software |
| 7 | Yossef Safout | Backend Developer | Software |
| 8 | Mohamed Abdel Ghani | Data Scientist | Data Science |

---

## Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/my-feature`)
3. **Commit** your changes (`git commit -m 'Add my feature'`)
4. **Push** to the branch (`git push origin feature/my-feature`)
5. **Open** a Pull Request

### Areas Where Help is Needed

- Adding new model builders (YOLO, ResNet, EfficientNet)
- Improving 3D machine visualization
- Writing educational component descriptions
- Adding translations
- Desktop application development (Electron)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Three.js](https://threejs.org/) — 3D WebGL rendering
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber/) — React renderer for Three.js
- [FastAPI](https://fastapi.tiangolo.com/) — Backend framework
- [React](https://react.dev/) — Frontend framework
- [Electron](https://www.electronjs.org/) — Desktop application framework

---

<p align="center">
  Made with ❤️ by <strong>DigiNeurons</strong> for African ML students and developers<br>
  <sub>🧠 NeuroScope — Learn by building, not by reading.</sub>
</p>
