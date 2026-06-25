#!/usr/bin/env python3
"""
NeuroScope Project Introduction PDF — Professional Centered Design
Edits: Hazem Khaled (was Hazem Khaled Ezzat Abdel Halim), Amr Mahmoud (was Omar)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

OUTPUT = "competition/NeuroScope_Project_Introduction_AYAIR2026.pdf"

PAGE_W, PAGE_H = A4
LM = 2.6*cm
RM = 2.6*cm
TM = 2.2*cm
BM = 2.0*cm
CW = PAGE_W - LM - RM

doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
                        leftMargin=LM, rightMargin=RM,
                        topMargin=TM, bottomMargin=BM)

# Colors
NAVY     = HexColor("#1B2A4A")
ACCENT   = HexColor("#3A7BD5")
MID_GRAY = HexColor("#444444")
LIGHT_GR = HexColor("#999999")
BORDER   = HexColor("#CBD5E1")
BG_CARD  = HexColor("#F7FAFC")

# Styles
sTitle = ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=26, leading=32,
                        textColor=NAVY, alignment=TA_CENTER, spaceAfter=2*mm)
sSub = ParagraphStyle("Sub", fontName="Helvetica", fontSize=11, leading=14,
                      textColor=ACCENT, alignment=TA_CENTER, spaceAfter=1*mm)
sComp = ParagraphStyle("Comp", fontName="Helvetica", fontSize=9, leading=12,
                       textColor=LIGHT_GR, alignment=TA_CENTER, spaceAfter=5*mm)
sSec = ParagraphStyle("Sec", fontName="Helvetica-Bold", fontSize=13, leading=18,
                      textColor=NAVY, alignment=TA_CENTER, spaceBefore=5*mm, spaceAfter=2.5*mm)
sBody = ParagraphStyle("B", fontName="Helvetica", fontSize=10, leading=14.5,
                       textColor=MID_GRAY, alignment=TA_JUSTIFY, spaceAfter=2.5*mm,
                       leftIndent=0.4*cm, rightIndent=0.4*cm)
sHL = ParagraphStyle("HL", fontName="Helvetica-Bold", fontSize=10.5, leading=15,
                     textColor=NAVY, alignment=TA_CENTER, spaceAfter=3*mm)
sMeta = ParagraphStyle("M", fontName="Helvetica", fontSize=10, leading=14,
                       textColor=MID_GRAY, alignment=TA_CENTER)
sName = ParagraphStyle("N", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
                       textColor=NAVY, alignment=TA_CENTER)
sRole = ParagraphStyle("R", fontName="Helvetica", fontSize=8, leading=11,
                       textColor=MID_GRAY, alignment=TA_CENTER)

def accent_line():
    return HRFlowable(width="35%", thickness=1.2, color=ACCENT, spaceBefore=2*mm, spaceAfter=2*mm)

def thin_line():
    return HRFlowable(width="80%", thickness=0.5, color=BORDER, spaceBefore=1*mm, spaceAfter=2*mm)

story = []

# ── HEADER ──
story.append(Spacer(1, 2*mm))
story.append(Paragraph("NeuroScope", sTitle))
story.append(Paragraph("Project Introduction", sSub))
story.append(Paragraph("AYAIR 2026 — Third Edition — Education Enhancement", sComp))
story.append(accent_line())

# ── META TABLE ──
meta = [
    ["Project Name", "NeuroScope"],
    ["Team Name", "DigiNeurons"],
    ["Category", "Education Enhancement"],
    ["Competition", "AYAIR 2026 — Third Edition"],
    ["Date", "June 2026"],
]
meta_t = Table([[Paragraph(f"<b>{r[0]}</b>", sMeta), Paragraph(r[1], sMeta)] for r in meta],
               colWidths=[4*cm, 8*cm])
meta_t.setStyle(TableStyle([
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LINEBELOW", (0,0), (-1,-2), 0.4, BORDER),
]))
story.append(meta_t)
story.append(Spacer(1, 5*mm))

# ── TEAM MEMBERS ──
story.append(Paragraph("Team Members", sSec))
story.append(Spacer(1, 2*mm))

team = [
    ("Hazem Khaled", "Technical Lead<br/>ML/DL Engineer"),
    ("Amr Mahmoud", "Backend<br/>Developer"),
    ("Shahd Khairy", "Frontend<br/>Developer"),
    ("Yomna Ashraf", "DL/ML Research<br/>Analyst"),
    ("Yossef Sharif", "Data Analyst<br/>&amp; QA"),
]
cells = [[Paragraph(n, sName), Spacer(1,1.5*mm), Paragraph(r, sRole)] for n, r in team]
cw = CW / 5
team_t = Table([cells], colWidths=[cw]*5)
team_t.setStyle(TableStyle([
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("LEFTPADDING", (0,0), (-1,-1), 4),
    ("RIGHTPADDING", (0,0), (-1,-1), 4),
    ("BACKGROUND", (0,0), (-1,-1), BG_CARD),
    ("BOX", (0,0), (-1,-1), 0.8, BORDER),
    ("LINEBEFORE", (1,0), (-1,-1), 0.4, BORDER),
]))
story.append(team_t)

# ── THE PROBLEM ──
story.append(Paragraph("The Problem We Solve", sSec))
story.append(thin_line())
story.append(Paragraph(
    "Millions of students across Africa and the world begin their journey into deep learning each year. "
    "They enroll in courses, attend university programs, and learn to write code like "
    "<font face='Courier' size='9'>model.fit()</font> to achieve high accuracy scores. "
    "But beneath this surface-level success lies a fundamental gap: "
    "<b>most students do not understand what happens inside the models they build.</b>", sBody))
story.append(Paragraph(
    "They copy architectures from GitHub without knowing why a ResNet uses skip connections, or why a "
    "transformer uses multi-head attention, or why batch normalization stabilizes training. When their model "
    "fails, they cannot diagnose the problem. The model is a black box — they can operate it, but they cannot "
    "see inside it.", sBody))
story.append(Paragraph(
    "This problem is especially acute in Africa. Egypt's Ministry of Communications and Information Technology "
    "has made digital transformation a national priority. Nigeria, Kenya, South Africa, Rwanda, and Tunisia are "
    "investing heavily in AI education. The African Union's Agenda 2063 and STISA 2034 strategy call for "
    "technically skilled youth to lead Africa's digital industrialization.", sBody))
story.append(Paragraph(
    "But the tools available to these students were not designed for them. Netron shows static two-dimensional "
    "diagrams with no explanation. TensorBoard is locked to TensorFlow and requires running training first. "
    "TensorSpace.js, which once offered three-dimensional visualization, has been abandoned since 2019. "
    "None of these tools explain what a layer does, detect architectural mistakes, work offline on a phone, "
    "or connect the visualization back to the student's actual code.", sBody))
story.append(Spacer(1, 2*mm))
story.append(Paragraph("NeuroScope changes this.", sHL))

# ── OUR SOLUTION ──
story.append(Paragraph("Our Solution", sSec))
story.append(thin_line())
story.append(Paragraph(
    "NeuroScope is a web-based tool and Visual Studio Code extension that transforms how students learn "
    "deep learning by making neural network architectures <b>visible, interactive, and understandable.</b>", sBody))
story.append(Paragraph(
    "A student uploads their model file — ONNX, PyTorch, Keras, or TensorFlow Lite — or opens their Python "
    "script or Jupyter notebook. NeuroScope parses the code and generates a <b>three-dimensional interactive "
    "visualization</b> of the architecture. Convolutional layers appear as boxes, fully connected layers as "
    "flat planes, recurrent layers as cylinders, and attention layers as octahedrons.", sBody))
story.append(Paragraph(
    "Clicking any three-dimensional component shows three things: a plain-language description of what that "
    "layer does, the exact code block that created it, and the layer's parameters, FLOPs, and memory footprint. "
    "This bidirectional mapping means a student can explore a transformer in 3D and understand the code, or "
    "read code and see the architecture.", sBody))
story.append(Paragraph(
    "The architecture health check engine detects over <b>forty-seven common anti-patterns</b>: missing activation "
    "functions, sigmoid in deep networks, missing skip connections, parameter explosion, redundant layers, and "
    "more. Each finding includes severity, explanation, and a suggested fix — like a spell-checker for neural "
    "network design.", sBody))
story.append(Paragraph(
    "The real-time simulation updates the three-dimensional visualization instantly when a student edits code — "
    "before running it. Changing the number of filters, adjusting dropout, or adding a layer immediately shows "
    "the architectural impact, developing intuition that would otherwise require months of trial and error.", sBody))
story.append(Paragraph(
    "When the student runs their code, NeuroScope animates the forward pass: data flows through the network as "
    "animated particles, tensor shapes change at each layer, and the student watches input transform into a "
    "prediction in real time.", sBody))

# ── IMPACT ──
story.append(Paragraph("Impact for Africa and the World", sSec))
story.append(thin_line())
story.append(Paragraph(
    "NeuroScope is <b>free, open-source, and designed for the environments where it is needed most.</b> It works "
    "entirely in the browser with no installation. It functions as a progressive web application that works "
    "offline — critical for areas with intermittent connectivity. It requires no GPU, no cloud credits, and no "
    "expensive licenses. It runs on a smartphone, a tablet, or a ten-year-old laptop.", sBody))
story.append(Paragraph(
    "It supports five languages: <b>English, French, Arabic, Swahili, and Portuguese</b> — covering Egypt's "
    "Arabic-speaking governorates, Francophone West and Central Africa, East Africa's Swahili-speaking regions, "
    "and Lusophone Southern Africa.", sBody))
story.append(Paragraph(
    "NeuroScope aligns with the AU's STISA 2034 priority of building scientific literacy, with Agenda 2063's "
    "call for inclusive development, and with Egypt's national digital transformation strategy. It addresses the "
    "mentorship gap: when no senior ML engineer is available to review a student's architecture, NeuroScope "
    "provides that review automatically and clearly.", sBody))
story.append(Paragraph(
    "But this tool is not only for Africa. Every student worldwide who struggles to understand why their network "
    "is not learning, or what each block in a transformer does, will benefit from NeuroScope.", sBody))

# ── SUSTAINABILITY ──
story.append(Paragraph("Sustainability", sSec))
story.append(thin_line())
story.append(Paragraph(
    "NeuroScope is released under the <b>MIT license</b> as a fully open-source project. University professors can "
    "integrate it into curricula, students can contribute new analysis rules and translations, and institutions "
    "can deploy their own instances.", sBody))
story.append(Paragraph(
    "We are building NeuroScope not just as a competition entry, but as <b>lasting infrastructure for deep "
    "learning education in Africa and beyond.</b>", sBody))

# Footer accent
story.append(Spacer(1, 8*mm))
story.append(accent_line())

doc.build(story)
print(f"✅ PDF generated: {OUTPUT}")
