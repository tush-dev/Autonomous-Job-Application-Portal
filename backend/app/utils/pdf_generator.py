from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Optional
import io


def generate_resume_pdf(content: dict, output_path: Optional[str] = None) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer if not output_path else output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    story = []

    name_style = ParagraphStyle(
        "Name",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=6,
        alignment=1,
    )

    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
        borderWidth=1,
        borderColor="#000000",
        borderPadding=4,
    )

    normal_style = styles["Normal"]

    story.append(Paragraph(content.get("name", ""), name_style))
    story.append(Paragraph(content.get("contact_info", ""), normal_style))
    story.append(Spacer(1, 12))

    for section in content.get("sections", []):
        story.append(Paragraph(section.get("title", ""), section_style))
        items = section.get("items", [])
        for item in items:
            if isinstance(item, str):
                story.append(Paragraph(f"• {item}", normal_style))
            elif isinstance(item, dict):
                line = item.get("title", "")
                if item.get("subtitle"):
                    line += f" — {item['subtitle']}"
                story.append(Paragraph(f"• {line}", normal_style))
        story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()
