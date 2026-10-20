#!/usr/bin/env python3
"""
clean_notebook_outputs.py  --  MAINTAINER tool (students do not need it)
========================================================================

Keep the committed notebooks small and tidy after you re-execute them.

    python tools/clean_notebook_outputs.py 2-mongodb-workshop/workbook.ipynb 4-neo4j-workshop/workbook.ipynb

What it does, for every notebook given on the command line:

1. Replaces the interactive ``neo4j_viz`` graph widgets in the saved outputs by a one-line note.
   Each widget embeds ~1.8 MB of JavaScript, so a notebook with six of them would weigh >10 MB in git.
   (The widget is re-created every time the cell is run, so students lose nothing.)
2. Deletes the per-cell execution timestamps (``metadata.execution``) that make git diffs noisy.

The text/table/figure outputs are kept on purpose: they are the "expected results" that
self-learners compare their own run with.
"""
import json
import sys
from pathlib import Path

PLACEHOLDER = "[Interactive graph: run this cell to draw it. The widget is not stored in the notebook file.]"


def clean(path: Path) -> None:
    nb = json.loads(path.read_text())
    stripped = 0
    for cell in nb["cells"]:
        cell.get("metadata", {}).pop("execution", None)
        for out in cell.get("outputs", []):
            html = out.get("data", {}).get("text/html")
            if html is not None and "NVLBase" in "".join(html):          # fingerprint of the neo4j_viz JavaScript bundle
                out["data"] = {"text/plain": [PLACEHOLDER]}
                stripped += 1
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    print(f"{path}: stripped {stripped} interactive graph output(s); now {path.stat().st_size / 1024:,.0f} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for name in sys.argv[1:]:
        clean(Path(name))
