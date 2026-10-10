import json
from schema import Document


def _lines(text: str):
    ls = text.split("\n")
    return [l + "\n" for l in ls[:-1]] + [ls[-1]]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(text)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": _lines(text)}


def render(doc: Document, path: str):
    cells = [md(f"# {doc.title}\n\n*{doc.subtitle}*")]
    for i, s in enumerate(doc.sections, 1):
        body = f"## {i}. {s.heading}\n\n" + "\n\n".join(s.paragraphs)
        if s.bullets:
            body += "\n\n" + "\n".join("- " + b for b in s.bullets)
        cells.append(md(body))
        if s.table and s.table.headers:
            n = len(s.table.headers)
            rows = [(list(r) + [""] * n)[:n] for r in s.table.rows]
            cells.append(code(f"headers = {s.table.headers!r}\nrows = {rows!r}\n\n"
                              "print(' | '.join(headers))\nfor r in rows:\n    print(' | '.join(r))"))
    nb = {"cells": cells, "nbformat": 4, "nbformat_minor": 4,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
