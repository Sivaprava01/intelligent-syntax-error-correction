"""App package initialization."""

import sys
from pathlib import Path

# Ensure project root is in sys.path regardless of where uvicorn is launched
_root = str(Path(__file__).resolve().parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from backend.app.main import app

__all__ = ["app"]
