"""Collect today's forecast/observation snapshot without opening VS Code.

Runs the code cells of notebooks/00_data_collection.ipynb (the single source of truth), so the
scheduled job and the notebook can never drift apart. Schedule it daily; see README.md.

Usage:  .venv\\Scripts\\python.exe collect_snapshot.py            (Windows)
        .venv/bin/python collect_snapshot.py                      (macOS / Linux)
Exit code 0 = snapshot complete/partial or already present, 1 = collection failed.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "notebooks" / "00_data_collection.ipynb"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # Task Scheduler consoles are not UTF-8
    os.environ["SURF_IR_LIBRARY_MODE"] = "0"
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.chdir(ROOT)
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    code = "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    namespace = {"__name__": "__main__"}
    exec(compile(code, str(NOTEBOOK), "exec"), namespace)
    status = namespace.get("SNAPSHOT_STATUS", "unknown")
    print(f"Snapshot status: {status}")
    return 1 if status == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
