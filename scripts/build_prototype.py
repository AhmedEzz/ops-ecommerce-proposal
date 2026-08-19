#!/usr/bin/env python3
"""
Build the single-file clickable prototype.

Injects the extracted (and anonymised) workbook data into the HTML template so
the deliverable is one self-contained file the client can open or forward with
no server, no CDN and no external assets.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "deliverables" / "data"
PROTO = ROOT / "deliverables" / "03-Prototype"
TEMPLATE = Path(__file__).resolve().parent / "prototype.template.html"
OUT = PROTO / "index.html"

MARKER = "/*__DATA__*/"


def main():
    payload = {
        "seed": json.loads((DATA / "seed.json").read_text(encoding="utf-8")),
        "metrics": json.loads((DATA / "metrics.json").read_text(encoding="utf-8")),
        "supporting": json.loads((DATA / "supporting.json").read_text(encoding="utf-8")),
        # The admin console's Business Rules screen shows the client's real
        # controlled vocabularies, so ship the enum profile too.
        "enums": json.loads((DATA / "enums.json").read_text(encoding="utf-8")),
    }

    html = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in html:
        raise SystemExit(f"marker {MARKER} not found in {TEMPLATE.name}")

    # separators=(',',':') keeps the embedded payload compact; ensure_ascii=False
    # preserves the Arabic governorate and area names.
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # The payload sits inside a <script> block, so any literal "</script>" in the
    # data would terminate it early. None exists today, but escape defensively.
    blob = blob.replace("</", "<\\/")

    OUT.write_text(html.replace(MARKER, blob), encoding="utf-8")

    size = OUT.stat().st_size
    print(f"wrote {OUT.relative_to(ROOT)}  ({size/1024:.0f} KB)")
    print(f"  seed rows      {len(payload['seed'])}")
    print(f"  vendors        {len({r['vendor'] for r in payload['seed']})}")
    print(f"  self-contained: no external requests")


if __name__ == "__main__":
    main()
