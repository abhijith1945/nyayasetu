"""Compatibility entrypoint for running NyayaSetu from the repository root.

This module exists so imports like `from main import supabase` continue to work
when the app is started as `uvicorn backend.main:app`.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

_ENV_PATH = Path(__file__).resolve().parent / "backend" / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase = None
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "your_supabase_url":
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

from backend.main import app  # noqa: E402

__all__ = ["app", "supabase"]
