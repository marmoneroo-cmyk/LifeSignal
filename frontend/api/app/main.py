"""FastAPI application entrypoint for the Health Intelligence MVP."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DISCLAIMER, get_settings
from app.db import Base, engine
from app.routers import (
    admin,
    auth,
    calendar_export,
    chat,
    documents,
    drug_search,
    family,
    goals,
    imports,
    insurance,
    labs,
    medications,
    report,
    share,
    users,
)

settings = get_settings()

# Create tables on startup (fine for SQLite/MVP; use Alembic for Postgres prod).
# Wrapped so a transient DB connection failure on a Vercel cold start does not
# crash the whole app (existing tables will still serve requests; missing ones
# can be retried on the next cold start).
import logging

try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:  # noqa: BLE001 — log and continue; don't kill the app
    logging.getLogger("lifesignal").warning(
        "Base.metadata.create_all failed at startup: %s", exc,
    )

app = FastAPI(
    title="Personal Health Intelligence API",
    version="0.1.0",
    description=(
        "Clinical Decision Support System (MVP). " + DISCLAIMER
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(labs.router)
app.include_router(insurance.router)
app.include_router(report.router)
app.include_router(documents.router)
app.include_router(medications.router)
app.include_router(family.router)
app.include_router(chat.router)
app.include_router(share.router)
app.include_router(goals.router)
app.include_router(calendar_export.router)
app.include_router(admin.router)
app.include_router(drug_search.router)
app.include_router(imports.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "disclaimer": DISCLAIMER}
