"""Prompt -> local LLM -> documents.

Examples:
  python test_run.py "Create a project report for an AI attendance system"
  python test_run.py "Budget for a college fest" --formats xlsx,csv --name fest_budget
  python test_run.py "Pitch deck for a study app" --type "Pitch Deck" --sections 8 --formats pptx
  python test_run.py "Annual report for a small bakery" --model qwen2.5:7b

Formats: docx doc odt pdf pptx xlsx csv html json xml py ipynb log zip (default: all)
"""
import argparse
import time

import llm
from llm import generate_document
from renderers import render_all, ALL_FORMATS

ap = argparse.ArgumentParser()
ap.add_argument("prompt")
ap.add_argument("--type", default="Project Report")
ap.add_argument("--formats", default="all")
ap.add_argument("--name", default="report")
ap.add_argument("--sections", type=int, default=6)
ap.add_argument("--model", default=None, help="Ollama model to use, e.g. qwen2.5:7b")
a = ap.parse_args()

if a.model:
    llm.MODEL = a.model
formats = ALL_FORMATS if a.formats == "all" else tuple(f.strip() for f in a.formats.split(","))

print(f"Model: {llm.MODEL}")
t0 = time.time()
doc = generate_document(a.prompt, a.type, a.sections,
                        on_progress=lambda i, n, h: print(f"[{i}/{n}] {h}"))
paths = render_all(doc, base=a.name, formats=formats)
print(f"\nDone in {time.time() - t0:.0f}s")
for f, p in paths.items():
    print(f"  {f.upper():6} -> {p}")
