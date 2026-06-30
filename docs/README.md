# NeuroScope — Documentation Index

**Last Updated:** June 30, 2026

---

## Documents

### Competition Submission
| Document | Path | Audience |
|----------|------|----------|
| **Project Introduction Essay** | `competition/NeuroScope_Essay_AYAIR2026.pdf` | Judges, AYAIR 2026 (Jotform submission) |
| **Project Paper** | `competition/NeuroScope_Project_Paper_AYAIR2026.pdf` | Judges, AYAIR 2026 (email after submission) |

### Business Documents
| Document | Path | Audience |
|----------|------|----------|
| **BRD** | `docs/brd/NeuroScope-BRD.md` | Stakeholders, judges, team leads |
| **PRD** | `docs/prd/NeuroScope-PRD.md` | Product owner, designers, developers |

### Technical Documents
| Document | Path | Audience |
|----------|------|----------|
| **Technical Architecture** | `docs/technical/NeuroScope-Technical-Architecture.md` | All developers — system architecture, tech stack, deployment |
| **API Reference** | `docs/technical/NeuroScope-API-Reference.md` | Backend team — endpoints, request/response, examples |
| **Frontend Guide** | `docs/technical/NeuroScope-Frontend-Guide.md` | Shahd — components, store, types, 3D rendering |
| **Data Science Guide** | `docs/technical/NeuroScope-DataScience-Guide.md` | Mohamed Abdel Ghani — model definitions, educational content, rules |

### Vision Documents
| Document | Path | Audience |
|----------|------|----------|
| **Detailed Vision (Arabic)** | `docs/neuroscope-vision-detailed-ar.md` | Full team |
| **Brief Vision (English)** | `docs/neuroscope-vision-brief.md` | Quick reference |

### Data Definitions
| File | Path | Purpose |
|------|------|---------|
| **CNN v16 Model Definition** | `src/data/models/cnn_v16.json` | Model layers, extensions, options, educational content |
| **Builder Rules** | `config/builder_rules.yaml` | Validation rules for common DL mistakes |
| **Layer Shapes** | `config/layer_shapes.yaml` | Layer → 3D shape mapping |
| **UI Strings (EN)** | `config/languages/en.json` | English UI text |

---

## Team Assignment

| Team Member | Role | Documents to Read |
|-------------|------|-------------------|
| **Hazem Khaled** | Lead | All documents |
| **Shahd Khairy** | Frontend | Technical Architecture + Frontend Guide + CNN v16 JSON |
| **Mohamed Wagdi** | Backend | Technical Architecture + API Reference + CNN v16 JSON |
| **Ziad Mohamed** | Backend | Technical Architecture + API Reference + builder_rules.yaml |
| **Yossef Safout** | Backend | Technical Architecture + API Reference + CNN v16 JSON |
| **Mohamed Abdel Ghani** | Data Science | Data Science Guide + CNN v16 JSON + builder_rules.yaml |
| **Yossef Shrif** | Data Analysis | BRD + PRD |
| **Yomna Ashraf** | Data Analysis | BRD + PRD |

---

## Quick Links

- **Repo:** https://github.com/hazemelerefey/neuroscope
- **API Docs:** `http://localhost:8000/docs` (FastAPI auto-generated)
- **Prototype:** `prototype/index.html`
- **Competition:** AYAIR 2026 — Education Enhancement
