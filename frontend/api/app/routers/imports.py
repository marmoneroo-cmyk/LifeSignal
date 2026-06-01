"""Specialty data imports: Apple Health, 23andMe genetic raw data.

Both endpoints accept the user's file upload, parse it, and return
review-ready data WITHOUT auto-saving. The user reviews the extracted
records on the frontend and explicitly confirms — same pattern as PDF
ingest, important for medical data.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import current_user
from app.ingest import apple_health, genetic_23andme
from app.models import User

router = APIRouter(prefix="/api/imports", tags=["imports"])

_MAX_BYTES = 50 * 1024 * 1024  # Apple exports can be large


@router.post("/apple-health")
async def import_apple_health(
    file: UploadFile = File(...),
    _account: User = Depends(current_user),
) -> dict:
    """Parse an Apple Health export (.xml or .zip containing export.xml).

    Returns daily-deduplicated samples for: blood pressure, glucose, BMI,
    heart rate, SpO2. The frontend lets the user pick which to save.
    """
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file.")
    if len(data) > _MAX_BYTES:
        raise HTTPException(413, f"File too large (max {_MAX_BYTES // 1024 // 1024} MB).")
    try:
        records = apple_health.parse(data)
    except Exception as exc:  # noqa: BLE001 — bubble up a clean message
        raise HTTPException(422, f"Could not read Apple Health export: {exc}")
    return {"filename": file.filename, "count": len(records), "records": records}


@router.post("/23andme")
async def import_23andme(
    file: UploadFile = File(...),
    lang: str = Form("he"),
    _account: User = Depends(current_user),
) -> dict:
    """Parse a 23andMe raw-data export.

    Returns notable SNPs found (curated list — never an interpretation).
    Includes an explicit disclaimer the frontend MUST show alongside results.
    """
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file.")
    if len(data) > _MAX_BYTES:
        raise HTTPException(413, f"File too large (max {_MAX_BYTES // 1024 // 1024} MB).")
    try:
        result = genetic_23andme.parse(data, lang=lang)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(422, f"Could not read 23andMe file: {exc}")
    result["disclaimer_he"] = (
        "המידע הגנטי הוא לעיון בלבד. אינו מהווה אבחנה רפואית או ייעוץ גנטי. "
        "להבנת ההשלכות יש להתייעץ עם יועץ/ת גנטי/ת מוסמך/ת."
    )
    result["disclaimer_en"] = (
        "Genetic information is informational only. Not a medical diagnosis "
        "or genetic counseling. For interpretation, consult a certified counselor."
    )
    result["filename"] = file.filename
    return result
