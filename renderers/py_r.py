import pprint
from schema import Document

SHOW = '''

def show(doc=DOCUMENT):
    """Print the document in the terminal."""
    print(doc["title"])
    print(doc["subtitle"])
    print("=" * 60)
    for i, sec in enumerate(doc["sections"], 1):
        print(f"\\n{i}. {sec['heading']}")
        for p in sec["paragraphs"]:
            print("  ", p)
        for b in sec["bullets"]:
            print("   -", b)
        t = sec.get("table")
        if t:
            print("   " + " | ".join(t["headers"]))
            for r in t["rows"]:
                print("   " + " | ".join(r))


if __name__ == "__main__":
    show()
'''


def render(doc: Document, path: str):
    clean = lambda s: " ".join(str(s).split())
    src = (f"# {clean(doc.title)}\n# {clean(doc.subtitle)}\n"
           "# Generated offline by Offline AI Document Generator.\n# Run: python this_file.py\n\n"
           "DOCUMENT = " + pprint.pformat(doc.model_dump(), width=100, sort_dicts=False) + "\n" + SHOW)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
