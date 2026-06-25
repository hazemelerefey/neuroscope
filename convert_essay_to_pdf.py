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
        .replace("\u2713", "[ok]")  # checkmark
        .replace("\u2717", "[x]")   # cross
    )


class EssayPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, sanitize("NeuroScope - Project Introduction Essay"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, sanitize("AYAIR 2026 - Education Enhancement Category"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_title(self, text):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 9, sanitize(text), align="C")
        self.ln(3)

    def add_subtitle(self, text):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, sanitize(text))
        self.ln(2)

    def add_body(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(40, 40, 40)
        text = sanitize(text)
        # Handle bold text marked with **
        parts = re.split(r'(\*\*.*?\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                self.set_font("Helvetica", "B", 10.5)
                self.write(5.5, part[2:-2])
                self.set_font("Helvetica", "", 10.5)
            else:
                self.write(5.5, part)
        self.ln(2)


# Read the essay
with open("competition/essay_final.md", "r", encoding="utf-8") as f:
    content = f.read()

# Parse sections
pdf = EssayPDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# Title
pdf.add_title("NeuroScope")
pdf.add_title("AI-Powered 3D Neural Network Architecture\nVisualizer and Analyzer")
pdf.ln(5)

# Metadata
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Project Name: NeuroScope", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Category: Education Enhancement", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Competition: AYAIR 2026 - Third Edition", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Date: June 2026", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(8)

# Parse markdown sections
sections = content.split("\n## ")
for i, section in enumerate(sections):
    if i == 0:
        continue  # Skip header metadata

    lines = section.strip().split("\n")
    title = lines[0].strip()
    pdf.add_subtitle(title)

    for line in lines[1:]:
        line = line.strip()
        if not line or line == "---":
            continue
        pdf.add_body(line)

# Save
output_path = "competition/NeuroScope_Project_Essay_AYAIR2026.pdf"
pdf.output(output_path)
print(f"PDF saved to: {output_path}")
print(f"Pages: {pdf.pages_count}")
