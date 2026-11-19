"""make.fun competition entry: copy the committed image into the output dir.

Deterministic: always writes the exact bytes of the committed ``entry.png``
that sits next to this script. Standard library only, no network access.

Output is written to ``$MAKEFUN_OUTPUT_DIR/entry.png`` when that variable is
set, otherwise to ``/output/entry.png``.
"""

import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")

    if not os.path.isfile(src):
        print("error: entry.png not found next to main.py", file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)

    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
