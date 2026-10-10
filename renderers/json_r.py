from schema import Document


def render(doc: Document, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc.model_dump_json(indent=2))
