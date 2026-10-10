import xml.etree.ElementTree as ET
from schema import Document


def render(doc: Document, path: str):
    root = ET.Element("document", title=doc.title, subtitle=doc.subtitle)
    for i, s in enumerate(doc.sections, 1):
        se = ET.SubElement(root, "section", id=str(i), heading=s.heading)
        for p in s.paragraphs:
            ET.SubElement(se, "paragraph").text = p
        if s.bullets:
            be = ET.SubElement(se, "bullets")
            for b in s.bullets:
                ET.SubElement(be, "bullet").text = b
        if s.table and s.table.headers:
            te = ET.SubElement(se, "table")
            he = ET.SubElement(te, "header")
            for c in s.table.headers:
                ET.SubElement(he, "cell").text = c
            for r in s.table.rows:
                re_ = ET.SubElement(te, "row")
                for c in r:
                    ET.SubElement(re_, "cell").text = str(c)
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
