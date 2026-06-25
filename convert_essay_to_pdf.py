"""Convert the NeuroScope essay to a professional PDF."""

from fpdf import FPDF
import re


def sanitize(text):
    """Replace Unicode chars that Helvetica can't handle."""
    return (text
        .replace("\u2014", " - ")   # em-dash
        .replace("\u2013", "-")     # en-dash
        .replace("\u2018", "'")     # left single quote
        .replace("\u2019", "'")     # right single quote
        .replace("\u201c", '"')     # left double quote
        .replace("\u201d", '"')     # right double quote
        .replace("\u2026", "...")   # ellipsis
        .replace("\u2022", "*")     # bullet
        .replace("\u2192", "->")    # arrow
    )


class EssayPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 7, sanitize("NeuroScope - Project Introduction"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, sanitize("AYAIR 2026 - Education Enhancement"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)
        self.set_draw_color(180, 180, 180)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_main_title(self, text):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 10, sanitize(text), align="C")
        self.ln(2)

    def add_subtitle_line(self, text):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, sanitize(text), align="C")
        self.ln(1)

    def add_section_heading(self, text):
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 60, 120)
        self.multi_cell(0, 8, sanitize(text))
        self.ln(2)

    def add_body(self, text):
        text = sanitize(text.strip())
        if not text:
            return

        self.set_text_color(40, 40, 40)

        # Handle bold text marked with **
        parts = re.split(r'(\*\*.*?\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                self.set_font("Helvetica", "B", 10.5)
                self.write(6, part[2:-2])
            else:
                self.set_font("Helvetica", "", 10.5)
                self.write(6, part)
        self.ln(7)


# Read the essay
with open("competition/essay_final.md", "r", encoding="utf-8") as f:
    content = f.read()

# Build PDF
pdf = EssayPDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# --- Title Block ---
pdf.ln(10)
pdf.add_main_title("NeuroScope")
pdf.add_main_title("AI-Powered 3D Neural Network Architecture\nVisualizer and Analyzer")
pdf.ln(6)

# Metadata block
pdf.set_draw_color(180, 180, 180)
pdf.set_fill_color(245, 247, 250)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(80, 80, 80)

meta_y = pdf.get_y()
pdf.rect(30, meta_y, 150, 30, style="F")
pdf.set_y(meta_y + 3)
pdf.cell(0, 6, "Project Name: NeuroScope", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Category: Education Enhancement", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Competition: AYAIR 2026 - Third Edition", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Date: June 2026", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(8)

# --- Body Sections ---
sections = content.split("\n## ")
for i, section in enumerate(sections):
    if i == 0:
        continue  # Skip header metadata

    lines = section.strip().split("\n")
    heading = lines[0].strip()
    pdf.add_section_heading(heading)

    for line in lines[1:]:
        line = line.strip()
        if not line or line == "---":
            continue
        pdf.add_body(line)

# Save
output_path = "competition/NeuroScope_Project_Introduction_AYAIR2026.pdf"
pdf.output(output_path)
print(f"PDF saved to: {output_path}")
print(f"Pages: {pdf.pages_count}")
