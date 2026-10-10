import os
import zipfile
from . import (docx_r, doc_r, odt_r, pdf_r, pptx_r, xlsx_r, csv_r,
               html_r, json_r, xml_r, py_r, ipynb_r, log_r)

RENDERERS = {
    "docx": docx_r, "doc": doc_r, "odt": odt_r, "pdf": pdf_r,
    "pptx": pptx_r, "xlsx": xlsx_r, "csv": csv_r, "html": html_r,
    "json": json_r, "xml": xml_r, "py": py_r, "ipynb": ipynb_r, "log": log_r,
}
ALL_FORMATS = tuple(RENDERERS) + ("zip",)


def render_all(doc, outdir="output", base="report", formats=ALL_FORMATS):
    """One Document JSON -> every requested format. 'zip' bundles all the others.
    Returns {format: path}."""
    os.makedirs(outdir, exist_ok=True)
    paths = {}
    for f in formats:
        if f == "zip":
            continue
        p = os.path.join(outdir, f"{base}.{f}")
        RENDERERS[f].render(doc, p)
        paths[f] = p
    if "zip" in formats:
        zp = os.path.join(outdir, f"{base}.zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for p in paths.values():
                z.write(p, arcname=os.path.basename(p))
        paths["zip"] = zp
    return paths
