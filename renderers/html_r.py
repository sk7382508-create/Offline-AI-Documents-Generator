from html import escape as e
from schema import Document

CSS = """
:root{--bg:#fff;--fg:#222;--accent:#1F3A5F;--row:#eef2f7;--line:#c9d1dc}
@media (prefers-color-scheme:dark){:root{--bg:#121417;--fg:#e8e8e8;--accent:#8fb4e8;--row:#1c2128;--line:#333b47}}
body{font-family:Segoe UI,Calibri,Arial,sans-serif;background:var(--bg);color:var(--fg);
max-width:860px;margin:0 auto;padding:40px 20px;line-height:1.65}
header{text-align:center;padding:60px 0;border-bottom:3px solid var(--accent);margin-bottom:30px}
h1{font-size:2.4rem;color:var(--accent);margin:0}h2{color:var(--accent);margin-top:36px}
.sub{font-size:1.15rem;opacity:.8}
table{border-collapse:collapse;width:100%;margin:14px 0;overflow-x:auto;display:block}
th{background:var(--accent);color:#fff;text-align:left}th,td{padding:8px 12px;border:1px solid var(--line)}
tr:nth-child(even) td{background:var(--row)}
footer{margin-top:50px;font-size:.8rem;opacity:.6;text-align:center}
"""


def render(doc: Document, path: str):
    h = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         f"<title>{e(doc.title)}</title><style>{CSS}</style></head><body>",
         f'<header><h1>{e(doc.title)}</h1><div class="sub">{e(doc.subtitle)}</div></header>']
    for i, s in enumerate(doc.sections, 1):
        h.append(f'<section id="s{i}"><h2>{i}. {e(s.heading)}</h2>')
        h += [f"<p>{e(p)}</p>" for p in s.paragraphs]
        if s.bullets:
            h.append("<ul>" + "".join(f"<li>{e(b)}</li>" for b in s.bullets) + "</ul>")
        if s.table and s.table.headers:
            n = len(s.table.headers)
            h.append("<table><thead><tr>" + "".join(f"<th>{e(c)}</th>" for c in s.table.headers)
                     + "</tr></thead><tbody>")
            for r in s.table.rows:
                h.append("<tr>" + "".join(f"<td>{e(str(c))}</td>" for c in (list(r) + [""] * n)[:n]) + "</tr>")
            h.append("</tbody></table>")
        h.append("</section>")
    h.append("<footer>Generated offline by Offline AI Document Generator</footer></body></html>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(h))
