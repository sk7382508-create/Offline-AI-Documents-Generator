import os
import ollama
from pydantic import ValidationError
from schema import Outline, Section, Document

MODEL = os.environ.get("DOCGEN_MODEL", "qwen2.5:3b")
SYSTEM = ("You are a professional technical writer. Reply ONLY with JSON that "
          "matches the requested schema. Write clear, formal, specific content.")


def _ask(prompt, model_cls, retries=3):
    """Call the local model, force JSON via schema, validate, retry on failure."""
    last_err = None
    for _ in range(retries):
        try:
            r = ollama.chat(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": prompt}],
                format=model_cls.model_json_schema(),
                options={"temperature": 0.3},
                keep_alive="30m",
            )
            return model_cls.model_validate_json(r["message"]["content"])
        except (ValidationError, ValueError) as e:
            last_err = e
    raise RuntimeError(f"Model failed after {retries} tries: {last_err}")


def generate_outline(request: str, doc_type: str = "Project Report", n: int = 6) -> Outline:
    prompt = (f"Document type: {doc_type}\nUser request: {request}\n\n"
              f"Create a title, a one-line subtitle and exactly {n} section headings.")
    try:
        return _ask(prompt, Outline)
    except RuntimeError:  # fallback so the demo never breaks
        return Outline(title=request[:60], subtitle=doc_type,
                       headings=["Introduction", "Objectives", "Methodology",
                                 "Implementation", "Results", "Conclusion"][:n])


def generate_section(request: str, doc_title: str, heading: str) -> Section:
    prompt = (f"Document: {doc_title}\nUser request: {request}\n\n"
              f"Write the section titled '{heading}'. Give 2 paragraphs (3-4 sentences each) "
              f"and 3-5 short bullet points. Add a table only if the section is naturally "
              f"tabular (headers + rows of short text), otherwise omit it. "
              f"Set heading to '{heading}'.")
    try:
        sec = _ask(prompt, Section)
        sec.heading = heading
        return sec
    except RuntimeError:
        return Section(heading=heading, paragraphs=["Content could not be generated for this section."])


def generate_document(request, doc_type="Project Report", n=6, on_progress=None) -> Document:
    outline = generate_outline(request, doc_type, n)
    return expand_outline(request, outline, on_progress)


def expand_outline(request, outline: Outline, on_progress=None) -> Document:
    sections = []
    for i, h in enumerate(outline.headings, 1):
        sections.append(generate_section(request, outline.title, h))
        if on_progress:
            on_progress(i, len(outline.headings), h)
    return Document(title=outline.title, subtitle=outline.subtitle, sections=sections)
