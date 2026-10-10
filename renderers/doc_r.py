"""Older Word format (.doc). Written as RTF, which Microsoft Word opens natively
as a normal .doc file. No extra software needed, fully offline."""
from schema import Document

BORDER = "".join(f"\\clbrd{s}\\brdrs\\brdrw10" for s in "tlbr")


def esc(text) -> str:
    out = []
    b = str(text).encode("utf-16-le")
    for i in range(0, len(b), 2):
        u = int.from_bytes(b[i:i + 2], "little")
        ch = chr(u)
        if ch in "\\{}":
            out.append("\\" + ch)
        elif ch == "\n":
            out.append("\\line ")
        elif u < 128:
            out.append(ch)
        else:
            out.append(f"\\u{u if u < 32768 else u - 65536}?")
    return "".join(out)


def render(doc: Document, path: str):
    r = ["{\\rtf1\\ansi\\ansicpg1252\\deff0{\\fonttbl{\\f0 Calibri;}}\n"]
    r.append("\\pard\\sb3600\\qc\\f0\\fs56\\b " + esc(doc.title) + "\\b0\\par\n")
    r.append("\\pard\\qc\\fs28 " + esc(doc.subtitle) + "\\par\n\\page\n")
    for i, sec in enumerate(doc.sections, 1):
        r.append("\\pard\\sb240\\sa120\\fs32\\b " + esc(f"{i}. {sec.heading}") + "\\b0\\par\n")
        for p in sec.paragraphs:
            r.append("\\pard\\sa120\\fs22 " + esc(p) + "\\par\n")
        for b in sec.bullets:
            r.append("\\pard\\li360\\fi-360\\sa60\\fs22 \\bullet\\tab " + esc(b) + "\\par\n")
        if sec.table and sec.table.headers:
            n = len(sec.table.headers)
            cells = "".join(f"{BORDER}\\cellx{9000 * (c + 1) // n}" for c in range(n))
            r.append("\\trowd\\trgaph108" + cells + "\n")
            for h in sec.table.headers:
                r.append("\\pard\\intbl\\b\\fs20 " + esc(h) + "\\b0\\cell\n")
            r.append("\\row\n")
            for row in sec.table.rows:
                row = (list(row) + [""] * n)[:n]
                r.append("\\trowd\\trgaph108" + cells + "\n")
                for v in row:
                    r.append("\\pard\\intbl\\fs20 " + esc(v) + "\\cell\n")
                r.append("\\row\n")
            r.append("\\pard\\par\n")
    r.append("}")
    with open(path, "w", encoding="ascii") as f:
        f.write("".join(r))
