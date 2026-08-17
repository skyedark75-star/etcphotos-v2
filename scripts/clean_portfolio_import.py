"""Remove temporary inbox copies only after an explicit confirmation phrase."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = (ROOT / "portfolio-import").resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm", default="", help="Must be exactly DELETE IMPORT COPIES")
    args = parser.parse_args()
    folders = [path for path in INBOX.iterdir() if path.is_dir()] if INBOX.exists() else []
    if args.confirm != "DELETE IMPORT COPIES":
        print("Dry run only. Would remove these inbox folders:")
        for folder in folders:
            print(f"- {folder.name}")
        print('Run again with --confirm "DELETE IMPORT COPIES" only after verifying the website import.')
        return 0
    for folder in folders:
        resolved = folder.resolve()
        if resolved.parent != INBOX:
            raise RuntimeError(f"Refusing unsafe cleanup target: {resolved}")
        shutil.rmtree(resolved)
        print(f"Removed temporary inbox copy: {folder.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
