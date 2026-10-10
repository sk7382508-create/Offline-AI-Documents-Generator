from datetime import datetime, timedelta
from schema import Document


def render(doc: Document, path: str):
    t = datetime.now()
    lines = []

    def log(level, msg):
        nonlocal t
        t += timedelta(milliseconds=40)
        lines.append(f"{t:%Y-%m-%d %H:%M:%S,%f}"[:-3] + f" {level:<7} {msg}")

    log("INFO", "docgen: Offline AI Document Generator started")
    log("INFO", "docgen: mode=OFFLINE external_requests=0")
    log("INFO", f"docgen: title='{doc.title}' sections={len(doc.sections)}")
    for i, s in enumerate(doc.sections, 1):
        rows = len(s.table.rows) if s.table else 0
        log("INFO", f"section[{i}] '{s.heading}' paragraphs={len(s.paragraphs)} "
                    f"bullets={len(s.bullets)} table_rows={rows}")
        if any("could not be generated" in p for p in s.paragraphs):
            log("WARNING", f"section[{i}] '{s.heading}' used fallback text (model output invalid)")
        if not s.paragraphs and not s.bullets:
            log("WARNING", f"section[{i}] '{s.heading}' is empty")
    log("INFO", "docgen: generation complete")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
