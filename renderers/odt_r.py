from odf.opendocument import OpenDocumentText
from odf.text import H, P
from odf.table import Table, TableColumn, TableRow, TableCell
from schema import Document


def render(doc: Document, path: str):
    d = OpenDocumentText()
    d.text.addElement(H(outlinelevel=1, text=doc.title))
    d.text.addElement(P(text=doc.subtitle))
    for i, sec in enumerate(doc.sections, 1):
        d.text.addElement(H(outlinelevel=2, text=f"{i}. {sec.heading}"))
        for p in sec.paragraphs:
            d.text.addElement(P(text=p))
        for b in sec.bullets:
            d.text.addElement(P(text="• " + b))
        if sec.table and sec.table.headers:
            n = len(sec.table.headers)
            t = Table(name=f"table{i}")
            t.addElement(TableColumn(numbercolumnsrepeated=n))
            for row in [sec.table.headers] + [(list(r) + [""] * n)[:n] for r in sec.table.rows]:
                tr = TableRow()
                for v in row:
                    tc = TableCell(valuetype="string")
                    tc.addElement(P(text=str(v)))
                    tr.addElement(tc)
                t.addElement(tr)
            d.text.addElement(t)
            d.text.addElement(P(text=""))
    d.save(path)
