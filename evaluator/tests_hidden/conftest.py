from __future__ import annotations

import os
import sys
from pathlib import Path


target = os.environ.get("EVAL_TARGET")
if target:
    sys.path.insert(0, str(Path(target).resolve()))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "solution"))
