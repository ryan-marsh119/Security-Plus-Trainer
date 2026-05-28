"""
Sets up Django so the MCP server can import models from the `questions `,
`progress`, and `users` apps. Must be imported BEFORE any model import.

This is the same setup `manage.py` does behind the scenes -- we just do it
explicitly because we don't have `manage.py` as our entry point.
"""

import os
import sys
from pathlib import Path

# Add backend/ to PYTHONPATH so `import questions.models` resolves.
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Point Djano at the same settings module manage.py uses.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "securityplus.settings")

import django # noqa: E402 (must come after sys.path/env tweaks)

django.setup()