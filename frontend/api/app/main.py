"""FastAPI application entrypoint for the Health Intelligence MVP."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DISCLAIMER, get_settings
from app.db import Base, engine
from app.routers import (
    auth,
    chat,
    documents,
    family,
    insurance,
    labs,
    medications,
    report,
    users,
)

settings = get_settings()

# Create tables on startup (fine for SQLite/MVP; use Alembic for Postgres prod).
Base.metadata.create_all(bind=engine)

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


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "disclaimer": DISCLAIMER}
