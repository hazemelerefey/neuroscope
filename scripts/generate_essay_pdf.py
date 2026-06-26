"""
Generate a professional PDF from the NeuroScope essay.
Uses reportlab (already in requirements.txt).
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import os
import re

# Paths
ESSAY_PATH = os.path.join(os.path.dirname(__file__), "..", "competition", "essay_final.md")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "competition")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "NeuroScope_Project_Introduction_AYAIR2026.pdf")


def read_essay(path: str) -> tuple[dict, str]:
    """Read the essay markdown and extract metadata + body."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract metadata from header
    metadata = {}
    lines = content.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---" and i > 5:
            body_start = i + 1
            break
        if line.startswith("**") and ":" in line:
            key = line.split("**")[1].split(":")[0].strip()
            val = line.split(":", 1)[1].strip().rstrip("*").strip("*")
            metadata[key] = val

    # Get body (skip title and metadata, skip footer)
    body_lines = lines[body_start:]
    # Remove trailing word count line
    while body_lines and body_lines[-1].strip().startswith("**Word Count"):
        body_lines.pop()
    while body_lines and body_lines[-1].strip() == "---":
        body_lines.pop()

    body = "\n".join(body_lines).strip()
    return metadata, body


def md_to_reportlab(text: str) -> str:
    """Convert markdown bold to reportlab XML tags, escaping HTML entities."""
    # Escape HTML entities first
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    # Convert markdown bold **text** to <b>text</b>
    # Use regex to find **...** patterns
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

    return text


def build_pdf(metadata: dict, body: str, output_path: str):
    """Build a professional PDF document."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        textColor=HexColor("#1a1a2e"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        textColor=HexColor("#4a4a6a"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )

    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=HexColor("#6a6a8a"),
        spaceAfter=2,
        alignment=TA_CENTER,
    )

    body_style = ParagraphStyle(
        "EssayBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        textColor=HexColor("#2a2a3a"),
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        firstLineIndent=0,
    )

    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=HexColor("#8a8aaa"),
        spaceBefore=20,
        alignment=TA_CENTER,
    )

    elements = []

    # Title
    elements.append(Paragraph("NeuroScope", title_style))
    elements.append(
        Paragraph("AI-Powered 3D Neural Network Architecture Visualizer and Analyzer", subtitle_style)
    )
    elements.append(Spacer(1, 8))

    # Divider
    elements.append(
        HRFlowable(width="60%", thickness=1, color=HexColor("#ccccdd"), spaceAfter=12, spaceBefore=4)
    )

    # Metadata
    for key, value in metadata.items():
        safe_value = md_to_reportlab(value)
        elements.append(Paragraph(f"<b>{key}:</b> {safe_value}", meta_style))

    elements.append(Spacer(1, 16))

    # Essay body — split into paragraphs
    paragraphs = body.split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Convert markdown to reportlab XML
        safe_para = md_to_reportlab(para)
        elements.append(Paragraph(safe_para, body_style))

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(
        HRFlowable(width="100%", thickness=0.5, color=HexColor("#ccccdd"), spaceAfter=8)
    )
    elements.append(Paragraph("DigiNeurons Team · AYAIR 2026 · Education Enhancement", footer_style))

    doc.build(elements)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    essay_path = os.path.abspath(ESSAY_PATH)
    output_path = os.path.abspath(OUTPUT_PDF)

    print(f"Reading essay from: {essay_path}")
    metadata, body = read_essay(essay_path)
    print(f"Metadata: {metadata}")
    print(f"Body length: {len(body)} chars")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    build_pdf(metadata, body, output_path)
