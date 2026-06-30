# NeuroScope — Business Requirements Document (BRD)

**Document Version:** 1.0
**Date:** June 29, 2026
**Prepared by:** Hazem Khaled — Team Leader, DigiNeurons
**Project:** NeuroScope — Visual Deep Learning Model Builder
**Competition:** AYAIR 2026 — Education Enhancement Category

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Objectives](#2-business-objectives)
3. [Project Scope](#3-project-scope)
4. [Stakeholders](#4-stakeholders)
5. [Current State Analysis](#5-current-state-analysis)
6. [Future State Vision](#6-future-state-vision)
7. [Functional Requirements](#7-functional-requirements)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Data Requirements](#9-data-requirements)
10. [Constraints & Assumptions](#10-constraints--assumptions)
11. [Risk Assessment](#11-risk-assessment)
12. [Success Metrics](#12-success-metrics)
13. [Timeline & Milestones](#13-timeline--milestones)
14. [Glossary](#14-glossary)

---

## 1. Executive Summary

NeuroScope is a **visual deep learning model builder** that enables ML students and developers to construct, configure, and understand neural network architectures through an interactive 3D interface — without writing code.

The tool addresses a critical gap: **ML students cannot visually understand what they are building.** They write layers in code, train models, and hope for the best. When something goes wrong — bad architecture, wasted compute, exploding memory — they have no way to know without senior engineering review. This gap is especially severe in Africa, where access to senior ML engineers is limited.

NeuroScope solves this by providing a **drag-and-drop visual builder** (inspired by n8n for workflows) where users select a model, configure hyperparameters through interactive 3D modules, and export a ready-to-run Jupyter Notebook. Every component includes educational explanations so students learn while building.

**Key Innovation:** NeuroScope does NOT run code or load datasets. It is a **code generation and education tool** — users export notebooks and run them on their own infrastructure (Google Colab, local machines, etc.).

---

## 2. Business Objectives

### Primary Objectives

| ID | Objective | Success Criteria |
|----|-----------|-----------------|
| BO-1 | Democratize deep learning model building for students with no coding experience | User can build a complete CNN training notebook without writing a single line of code |
| BO-2 | Reduce the learning curve for ML model configuration | Student understands what each hyperparameter does within 5 minutes of using the tool |
| BO-3 | Provide educational value through every interaction | Every option/spec has a plain-language explanation with real-world consequences |
| BO-4 | Win AYAIR 2026 Education Enhancement category | Project scores high on innovation, impact, and technical execution |

### Secondary Objectives

| ID | Objective | Success Criteria |
|----|-----------|-----------------|
| BO-5 | Build a reusable visual builder framework | New model families (YOLO, ResNet) can be added with minimal code changes |
| BO-6 | Support African ML students specifically | Tool works offline, supports multiple languages, runs on low-spec hardware |
| BO-7 | Create an open-source community around the tool | GitHub stars, forks, and contributions after competition |

---

## 3. Project Scope

### In Scope (Phase 1 — CNN v16)

| Feature | Description |
|---------|-------------|
| **Visual Workspace** | Empty canvas with `+` button, drag-and-drop model placement |
| **Model Selection** | CNN v16 as the first (and only) model family |
| **Core Engine 3D** | Interactive 3D block that activates when model is selected |
| **Extensions System** | Hyperparameter modules (Optimizer, Activation, Loss, etc.) with visual cables |
| **Configuration Panels** | Right-side panels for each extension with options and educational info |
| **Info Panel** | Model details + head layer info + extension summaries |
| **Notebook Window** | Collapsible code viewer with auto-injection on every change |
| **Export** | Jupyter Notebook (.ipynb) and Model YAML |
| **Educational Layer** | Every option has: what it is, when to use it, what happens if you choose wrong |
| **Develop Mode** | Layer-level view with freeze/unfreeze/remove/add capabilities |

### Out of Scope (Future Phases)

| Feature | Target Phase |
|---------|-------------|
| YOLO, ResNet, EfficientNet model families | Phase 2 |
| Multi-modal (multiple models in one pipeline) | Phase 2 |
| GPU backend for running code in-browser | Phase 3 |
| Model comparison (side-by-side) | Phase 2 |
| VS Code Extension | Phase 3 |
| AI Agent Plugins | Phase 3 |
| Desktop Application | Phase 3 |
| Dataset import and management | Never (out of tool scope) |
| Model training/execution | Never (out of tool scope) |

---

## 4. Stakeholders

### Internal Stakeholders

| Stakeholder | Role | Interest |
|-------------|------|----------|
| **Hazem Khaled** | Team Leader, Product Owner | Vision, architecture, quality, competition strategy |
| **Shahd Khairy** | Frontend Developer | 3D visualization, React components, UI/UX |
| **Mohamed Wagdi** | Backend Developer | API routes, model parsing, data processing |
| **Ziad Mohamed** | Backend Developer | Infrastructure, deployment, CI/CD |
| **Yossef Safout** | Backend Developer | Analysis engine, rules, export |
| **Ahmed Ali** | Data Scientist | Model analysis, architecture patterns |
| **Mohamed Abdel Ghani** | Data Scientist | Anti-pattern research, technical docs |
| **Yossef Shrif** | Data Analyst | Testing, validation, documentation |
| **Yomna Ashraf** | Data Analyst | Educational content, research |

### External Stakeholders

| Stakeholder | Role | Interest |
|-------------|------|----------|
| **AYAIR 2026 Judges** | Competition evaluators | Innovation, impact, technical execution |
| **ML Students (Africa)** | End users | Easy-to-use learning tool |
| **ML Educators** | Indirect users | Teaching aid for deep learning courses |
| **Dr. Tarek Ghoneimy** | Academic Supervisor | Academic rigor, project quality |

---

## 5. Current State Analysis

### What Exists (Chapter 1-4 of NeuroScope)

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI backend | ✅ Complete | Upload, analyze, export, compare routes |
| ONNX Parser | ✅ Complete | Full model parsing |
| PyTorch Parser | ✅ Complete | Full model parsing |
| Keras Parser | ✅ Complete | Full model parsing |
| TFLite Parser | ✅ Complete | Full model parsing |
| 3D Visualization (Three.js) | ✅ Complete | Basic cube rendering |
| Analysis Engine | ✅ Complete | 47+ rules across 3 categories |
| FLOPs Calculator | ✅ Complete | Per-layer computation |
| Memory Estimator | ✅ Complete | Per-layer memory footprint |
| Export (PDF, Markdown) | ✅ Complete | Report generation |
| i18n (5 languages) | ✅ Complete | EN, FR, AR, SW, PT |
| Docker setup | ✅ Complete | Backend + Frontend + Nginx |
| Prototype (Three.js) | ✅ Complete | Standalone visual builder demo |
| Security audit | ✅ Complete | 4 P0 + 6 P1 issues fixed |

### What's Changing

The project is **pivoting** from an "upload and analyze" tool to a "visual model builder." The existing backend infrastructure (parsers, analysis engine, export) will be adapted, but the frontend experience is completely redesigned.

| Old (Analyzer) | New (Visual Builder) |
|----------------|---------------------|
| Upload a model file | Select and configure a model visually |
| See what's already built | Build from scratch with guidance |
| Post-training analysis | Pre-training configuration |
| Code review tool | Code generation tool |

---

## 6. Future State Vision

### The User Journey

```
1. User opens NeuroScope → Empty workspace with + button
2. Clicks + or drags from right panel → Model selection menu opens
3. Selects CNN v16 → Core Engine activates (3D, glowing, labeled)
4. Extensions auto-load around the engine (Optimizer, Activation, Loss, etc.)
5. User clicks each extension → Panel opens with options + explanations
6. User selects options → Code injects into notebook, info panel updates
7. All extensions configured → Model complete
8. User exports → .ipynb file ready for Colab
9. User opens Colab → Adds dataset imports → Runs training
```

### The Metaphor

**Powering up a machine.** Dark to light. Disconnected to connected. Empty to complete. Every visual change = a line of code written. Every glow = a decision made with understanding.

---

## 7. Functional Requirements

### 7.1 Workspace Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-WS-01 | System SHALL display an empty workspace with a `+` button in the center on first load | P0 |
| FR-WS-02 | System SHALL provide a collapsible right panel showing available model families | P0 |
| FR-WS-03 | User SHALL be able to place a model by clicking `+` and selecting OR by dragging from the right panel | P0 |
| FR-WS-04 | Right panel SHALL hide after a model is placed | P0 |
| FR-WS-05 | System SHALL support repositioning of the core engine and extension blocks on the canvas | P1 |

### 7.2 Model Selection

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MS-01 | System SHALL support CNN v16 as the first model family | P0 |
| FR-MS-02 | Model selection menu SHALL appear in a hierarchical flow: Family → (Version → Size if applicable) | P0 |
| FR-MS-03 | If a model has no versions/sizes, selecting it SHALL immediately activate the core engine | P0 |
| FR-MS-04 | System SHALL display model metadata (name, type, default parameters) upon selection | P0 |
| FR-MS-05 | User SHALL be able to change the model by clicking the core engine block | P0 |

### 7.3 Core Engine

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CE-01 | Core engine SHALL render as a 3D block with power-on animation when model is selected | P0 |
| FR-CE-02 | Core engine SHALL display the model name/label on its surface | P0 |
| FR-CE-03 | Clicking the core engine SHALL open a context menu with options: Change Model, Custom (Develop Mode) | P0 |
| FR-CE-04 | Core engine size/complexity SHALL visually reflect model complexity (more layers = more 3D detail) | P1 |
| FR-CE-05 | Core engine SHALL display the Head layer information prominently | P0 |

### 7.4 Extensions System

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EX-01 | System SHALL load model-specific extensions when a model is selected | P0 |
| FR-EX-02 | Each extension SHALL render as a 3D satellite block connected to the core engine by a cable | P0 |
| FR-EX-03 | Each extension SHALL have a category color (Green=Training, Purple=Data, Yellow=Functional, Blue=Core) | P0 |
| FR-EX-04 | Clicking an extension SHALL open a right-side configuration panel | P0 |
| FR-EX-05 | Configuration panel SHALL display all available options with radio buttons or toggles | P0 |
| FR-EX-06 | Each option SHALL have an educational description (what, when, consequences) | P0 |
| FR-EX-07 | Selecting an option and clicking Apply SHALL inject code into the notebook | P0 |
| FR-EX-08 | Applied extension SHALL glow its category color and its cable SHALL illuminate | P0 |
| FR-EX-09 | Extension configuration SHALL be added to the Info Panel | P0 |
| FR-EX-10 | User SHALL be able to change an extension's configuration at any time | P0 |

### 7.5 CNN v16 Extensions

| ID | Extension | Category | Options | Priority |
|----|-----------|----------|---------|----------|
| FR-CNN-01 | Optimizer | Training (Green) | SGD, Adam, AdamW, RMSprop | P0 |
| FR-CNN-02 | Activation Function | Training (Green) | ReLU, LeakyReLU, SiLU, Mish, GELU | P0 |
| FR-CNN-03 | Loss Function | Training (Green) | CrossEntropy, FocalLoss, LabelSmoothing | P0 |
| FR-CNN-04 | Learning Rate | Training (Green) | 0.1, 0.01, 0.001, 0.0001 (with custom input) | P0 |
| FR-CNN-05 | Batch Size | Functional (Yellow) | 8, 16, 32, 64, 128 (with custom input) | P0 |
| FR-CNN-06 | Epochs | Functional (Yellow) | 50, 100, 200, 500 (with custom input) | P0 |
| FR-CNN-07 | Data Augmentation | Data (Purple) | None, Basic, Advanced, Custom | P1 |

### 7.6 Info Panel

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-IP-01 | Info Panel SHALL display model name, type, and architecture summary on model load | P0 |
| FR-IP-02 | Info Panel SHALL display Head layer details: default configuration, activation function, output neurons | P0 |
| FR-IP-03 | Info Panel SHALL update when any extension is configured | P0 |
| FR-IP-04 | Info Panel SHALL show brief, point-form information (not paragraphs) | P0 |
| FR-IP-05 | Info Panel SHALL be visible at all times (not hidden behind panels) | P0 |

### 7.7 Notebook Window

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-NB-01 | Notebook window SHALL be collapsible in the top-right corner of the UI | P0 |
| FR-NB-02 | Notebook window SHALL auto-open when a model is selected | P0 |
| FR-NB-03 | Notebook window SHALL auto-open when any extension is configured (code updates live) | P0 |
| FR-NB-04 | Notebook window SHALL support manual open/close by the user | P0 |
| FR-NB-05 | Notebook SHALL display generated Python code with syntax highlighting | P0 |
| FR-NB-06 | Notebook code SHALL be editable by the user | P0 |
| FR-NB-07 | Notebook SHALL include markdown comments explaining each code block | P1 |

### 7.8 Export

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EX-01 | System SHALL export as Jupyter Notebook (.ipynb) | P0 |
| FR-EX-02 | System SHALL export as Model YAML | P0 |
| FR-EX-03 | Exported notebook SHALL include all configured hyperparameters | P0 |
| FR-EX-04 | Exported notebook SHALL include placeholder comments for dataset import | P0 |
| FR-EX-05 | Exported notebook SHALL include placeholder comments for environment setup (if running locally) | P1 |

### 7.9 Develop Mode

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DM-01 | Develop Mode SHALL display all model layers in a list/tree view | P0 |
| FR-DM-02 | User SHALL be able to freeze/unfreeze individual layers | P0 |
| FR-DM-03 | User SHALL be able to remove layers | P1 |
| FR-DM-04 | User SHALL be able to add layers from a predefined library | P1 |
| FR-DM-05 | Head layer SHALL be prominently displayed with its default configuration | P0 |
| FR-DM-06 | Changes in Develop Mode SHALL update the notebook code | P0 |

### 7.10 Educational Layer

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ED-01 | Every extension option SHALL have a plain-language description | P0 |
| FR-ED-02 | Every option SHALL include "when to use" guidance | P0 |
| FR-ED-03 | Every option SHALL include "what happens if you choose wrong" consequences | P0 |
| FR-ED-04 | Educational content SHALL be accessible without leaving the configuration panel | P0 |
| FR-ED-05 | Head layer SHALL have a dedicated educational explanation | P0 |

---

## 8. Non-Functional Requirements

### 8.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-P-01 | Page load time (initial) | < 3 seconds |
| NFR-P-02 | Model selection to engine activation | < 1 second |
| NFR-P-03 | Extension click to panel open | < 500ms |
| NFR-P-04 | Code injection to notebook update | < 300ms |
| NFR-P-05 | 3D rendering frame rate | ≥ 30 FPS on integrated GPU |
| NFR-P-06 | Export generation time | < 2 seconds |

### 8.2 Usability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-U-01 | First-time user can build a complete model | Within 10 minutes without documentation |
| NFR-U-02 | Educational content readability | Grade 8 reading level (Flesch-Kincaid) |
| NFR-U-03 | Mobile responsiveness | Functional on tablets (1024px+) |
| NFR-U-04 | Accessibility | WCAG 2.1 AA compliance |

### 8.3 Compatibility

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-C-01 | Browser support | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |
| NFR-C-02 | WebGL support | Required (Three.js dependency) |
| NFR-C-03 | Exported notebook compatibility | Jupyter Notebook 6+, Google Colab |
| NFR-C-04 | Exported YAML compatibility | PyTorch 2.0+, Ultralytics 8.0+ |

### 8.4 Security

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-S-01 | No server-side code execution | Client-side only (static site) |
| NFR-S-02 | No user data collection | No analytics, no tracking |
| NFR-S-03 | No external API calls (except export) | All processing in-browser |
| NFR-S-04 | Content Security Policy | Strict CSP headers |

---

## 9. Data Requirements

### 9.1 Model Definitions

Each model family requires a JSON/YAML definition file containing:

```yaml
model:
  id: "cnn_v16"
  name: "CNN v16"
  family: "CNN"
  version: "16"
  sizes: null  # No size variants for CNN
  description: "16-layer Convolutional Neural Network for image classification"
  head:
    default_activation: "softmax"
    output_neurons: "num_classes"  # Dynamic based on user's dataset
    description: "Classification head — outputs probability for each class"
  layers:
    - name: "Conv2d_1"
      type: "conv2d"
      params: { in_channels: 3, out_channels: 64, kernel_size: 3, padding: 1 }
    - name: "BatchNorm_1"
      type: "batchnorm"
      params: { num_features: 64 }
    # ... all 16 layers
  extensions:
    - id: "optimizer"
      name: "Optimizer"
      category: "training"
      color: "green"
      options:
        - id: "sgd"
          name: "SGD"
          description: "Stochastic Gradient Descent — the classic optimizer"
          when_to_use: "When you have a well-tuned learning rate schedule"
          consequences: "Can be slow to converge; may get stuck in local minima"
          code: "optimizer = 'SGD'"
        - id: "adam"
          name: "Adam"
          # ...
    - id: "activation"
      # ...
```

### 9.2 Educational Content

Each option in each extension requires:

| Field | Description | Example |
|-------|-------------|---------|
| `description` | What it is (plain language) | "AdamW decouples weight decay from gradient updates" |
| `when_to_use` | Practical guidance | "Best for most modern architectures; default choice" |
| `consequences` | What happens if you choose wrong | "Using SGD without a good LR schedule can lead to very slow convergence" |
| `code_snippet` | The actual code line to inject | `optimizer = 'AdamW'` |

### 9.3 No User Data

NeuroScope does NOT collect, store, or transmit any user data. All processing happens in the browser. The exported notebook is the only output.

---

## 10. Constraints & Assumptions

### Constraints

| ID | Constraint | Impact |
|----|-----------|--------|
| CON-1 | Client-side only (no backend server for the visual builder) | All 3D rendering and code generation happens in the browser |
| CON-2 | WebGL required | Tool won't work on devices without WebGL support |
| CON-3 | CNN v16 is the only model for Phase 1 | Limits initial user base to CNN users |
| CON-4 | No dataset import or model execution | Users must handle dataset setup themselves |
| CON-5 | Competition deadline: June 30, 2026 (essay) | Phase 1 must be demonstrable |
| CON-6 | Team of 9 with varying skill levels | Some members are students with limited experience |

### Assumptions

| ID | Assumption | Risk if Wrong |
|----|-----------|---------------|
| ASM-1 | Users have basic understanding of deep learning concepts | Need more educational content |
| ASM-2 | Users will run exported notebooks on Colab or locally | May need to support other platforms |
| ASM-3 | CNN v16 architecture is well-defined and stable | May need to redesign model definition format |
| ASM-4 | Three.js can handle the 3D rendering requirements | May need to simplify visuals |
| ASM-5 | Users prefer visual configuration over writing code | May need to offer both modes |

---

## 11. Risk Assessment

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-1 | Three.js performance issues on low-end devices | Medium | High | Implement quality settings; fallback to 2D mode |
| R-2 | CNN v16 definition changes during development | Low | Medium | Use flexible JSON/YAML schema; version the definitions |
| R-3 | Team members unable to complete assigned tasks | Medium | High | Cross-training; clear documentation; daily standups |
| R-4 | Competition judges don't understand the visual metaphor | Low | High | Include demo video; clear educational explanations |
| R-5 | Exported notebooks don't run correctly on Colab | Low | High | Test exported notebooks on Colab before submission |
| R-6 | Scope creep (adding features beyond Phase 1) | High | Medium | Strict phase boundaries; defer to future phases |
| R-7 | Browser compatibility issues | Low | Medium | Test on all major browsers; use polyfills if needed |

---

## 12. Success Metrics

### Competition Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| AYAIR 2026 submission | Accepted for next phase | Pass/fail |
| Demo completeness | All P0 features working | Feature checklist |
| Educational value | Judges can understand the tool without documentation | Usability test |
| Innovation score | "Like n8n but for neural networks" | Judge feedback |

### Product Metrics (Post-Competition)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first model | < 10 minutes | User testing |
| Code correctness | Exported notebook runs without errors | Colab testing |
| Educational effectiveness | User can explain what each hyperparameter does | Quiz/survey |
| GitHub engagement | 50+ stars in first month | GitHub analytics |

---

## 13. Timeline & Milestones

### Phase 1: CNN v16 Visual Builder

| Date | Milestone | Deliverable |
|------|-----------|-------------|
| Jun 29, 2026 | Documentation complete | BRD, PRD, Technical Docs |
| Jun 30, 2026 | AYAIR essay deadline | Essay + prototype demo |
| Jul 1-7, 2026 | Frontend architecture | React + Three.js project setup |
| Jul 8-14, 2026 | Core engine + workspace | 3D model, drag-drop, model selection |
| Jul 15-21, 2026 | Extensions system | All CNN v16 extensions with panels |
| Jul 22-28, 2026 | Notebook + export | Code generation, .ipynb export |
| Jul 29-31, 2026 | Testing + polish | Bug fixes, performance, usability |

### Phase 2: Expansion (Post-Competition)

| Target | Feature |
|--------|---------|
| Aug 2026 | YOLO model family |
| Sep 2026 | ResNet, EfficientNet |
| Oct 2026 | Multi-modal, model comparison |
| Nov 2026 | VS Code Extension |

### Phase 3: Ecosystem

| Target | Feature |
|--------|---------|
| Dec 2026 | AI Agent Plugins |
| Jan 2027 | Desktop Application |
| Feb 2027 | GPU Backend |

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **Core Engine** | The central 3D block representing the selected model |
| **Extension** | A satellite 3D block representing a configurable hyperparameter |
| **Cable** | A visual connection between an extension and the core engine |
| **Head Layer** | The final layer of a neural network that produces output predictions |
| **Develop Mode** | Advanced view showing all model layers with edit capabilities |
| **Info Panel** | A sidebar displaying model and configuration details |
| **Notebook Window** | A collapsible code viewer showing generated Python code |
| **CNN v16** | A 16-layer Convolutional Neural Network — the first supported model |
| **Hyperparameter** | A configuration option that affects how a model trains |
| **Activation Function** | A mathematical function that determines neuron output |
| **Loss Function** | A function that measures how wrong the model's predictions are |
| **Optimizer** | An algorithm that adjusts model weights to minimize loss |

---

*Document prepared for DigiNeurons team and AYAIR 2026 competition.*
*For questions, contact: hazemelerefy@gmail.com*
