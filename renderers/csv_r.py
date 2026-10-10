import csv
from schema import Document


def render(doc: Document, path: str):
    """Block 1: overview of all sections. Then one block per table. Opens cleanly in Excel."""
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig = Excel-safe
        w = csv.writer(f)
        w.writerow([doc.title]); w.writerow([doc.subtitle]); w.writerow([])
        w.writerow(["#", "Section", "Summary", "Key Points"])
        for i, s in enumerate(doc.sections, 1):
            w.writerow([i, s.heading, s.paragraphs[0] if s.paragraphs else "",
                        " | ".join(s.bullets)])
        for s in doc.sections:
            if s.table and s.table.headers:
                n = len(s.table.headers)
                w.writerow([]); w.writerow([f"TABLE: {s.heading}"])
                w.writerow(s.table.headers)
                for r in s.table.rows:
                    w.writerow((list(r) + [""] * n)[:n])
