"""Vercel serverless entry point for the AlphaQuantPro FastAPI backend.

Vercel's Python runtime serves the ASGI ``app`` exported here.

IMPORTANT serverless caveats (see docs/DEPLOYMENT_vercel.md):
- Background paper-run threads do NOT persist across serverless invocations,
  so long-running paper/simulation runs are unreliable on Vercel. For the full
  experience, host the backend on a long-running platform instead.
- The serverless filesystem is ephemeral; set DATABASE_URL to an external
  database (e.g. Postgres) for durable storage. Without it, SQLite falls back
  to /tmp and is reset frequently.
"""
import os
import sys

# Ensure the `app` package is importable when Vercel runs this file.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402

__all__ = ["app"]
