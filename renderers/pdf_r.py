from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, ListFlowable, ListItem)
from schema import Document

NAVY = colors.HexColor("#1F3A5F")


def render(doc: Document, path: str):
    ss = getSampleStyleSheet()
    title = ParagraphStyle("T", parent=ss["Title"], fontSize=28, textColor=NAVY, spaceAfter=12)
    sub = ParagraphStyle("S", parent=ss["Normal"], fontSize=14, alignment=1)
    h1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=NAVY, spaceBefore=14)
    body = ParagraphStyle("B", parent=ss["Normal"], fontSize=11, leading=16, spaceAfter=6)
    cell = ParagraphStyle("C", parent=body, fontSize=9, leading=12, spaceAfter=0)
    cell_h = ParagraphStyle("CH", parent=cell, textColor=colors.white, fontName="Helvetica-Bold")

    story = [Spacer(1, 6 * cm), Paragraph(escape(doc.title), title),
             Paragraph(escape(doc.subtitle), sub), PageBreak()]

    for i, sec in enumerate(doc.sections, 1):
        story.append(Paragraph(f"{i}. {escape(sec.heading)}", h1))
        for p in sec.paragraphs:
            story.append(Paragraph(escape(p), body))
        if sec.bullets:
            story.append(ListFlowable(
                [ListItem(Paragraph(escape(b), body)) for b in sec.bullets],
                bulletType="bullet", start="•"))
        if sec.table and sec.table.headers:
            n = len(sec.table.headers)
            data = [[Paragraph(escape(h), cell_h) for h in sec.table.headers]]
            for row in sec.table.rows:
                row = (list(row) + [""] * n)[:n]
                data.append([Paragraph(escape(str(c)), cell) for c in row])
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2F7")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story += [Spacer(1, 8), t, Spacer(1, 8)]

    def footer(canvas, d):
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(A4[0] / 2, 1.2 * cm, f"Page {d.page - 1}")

    SimpleDocTemplate(path, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                      topMargin=2 * cm, bottomMargin=2 * cm, title=doc.title
                      ).build(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
