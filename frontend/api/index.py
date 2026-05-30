"""Vercel Python serverless entry point for the FastAPI backend.

Vercel auto-detects Python files inside `api/` and serves them as serverless
functions. The exported `app` is the FastAPI ASGI application — Vercel's Python
runtime handles ASGI apps natively, so every request to /api/* lands here and
is routed by FastAPI's internal router.

The vercel.json sibling file rewrites all /api/* to /api/index so the entire
FastAPI app (with its own /api/users, /api/auth, etc routers) responds.
"""
from __future__ import annotations

import os
import sys

# Make `app.*` imports resolve to /api/app/* (this file lives in /api/index.py
# and `app` is at /api/app/). Without this, Python would look for `app` in PWD.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# Import the FastAPI application. Vercel detects the `app` symbol as an
# ASGI app and routes all incoming requests to it.
from app.main import app  # noqa: E402, F401  re-exported as the Vercel handler
