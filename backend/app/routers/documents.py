"""Document Intake endpoint — upload a PDF, get back review-ready candidates.

Deliberately does NOT persist anything: it returns extracted lab/policy candidates
that the user reviews and then commits via the existing /labs and /policies
endpoints. This keeps a human in the loop, which matters for medical data.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import current_user
from app.ingest import pdf_parser
from app.ingest.table_extractor import extract as table_extract
from app.models import User

router = APIRouter(prefix="/api/documents", tags=["documents"])

_MAX_BYTES = 20 * 1024 * 1024  # 20 MB (Excel files can be larger)
_ALLOWED_KINDS = {"lab", "insurance", "auto"}
_EXCEL_TYPES = {".xlsx", ".xls", ".ods"}
_EXCEL_MIMES = {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel", "application/octet-stream"}


@router.post("/extract")
async def extract(
    file: UploadFile = File(...),
    kind: str = Form("auto"),
    _account: User = Depends(current_user),
) -> dict:
    if kind not in _ALLOWED_KINDS:
        raise HTTPException(422, f"kind must be one of {sorted(_ALLOWED_KINDS)}")

    filename = file.filename or ""
    fn_lower = filename.lower()
    is_excel = any(fn_lower.endswith(ext) for ext in _EXCEL_TYPES)
    is_pdf = fn_lower.endswith(".pdf") or (file.content_type or "").startswith("application/pdf")

    if not is_excel and not is_pdf:
        raise HTTPException(415, "נתמכים: PDF ו-Excel (.xlsx)")

    data = await file.read()
    if len(data) > _MAX_BYTES:
        raise HTTPException(413, "קובץ גדול מדי (מקסימום 20MB).")
    if not data:
        raise HTTPException(400, "קובץ ריק.")

    try:
        if is_excel:
            # Smart table extraction — uses the document's own reference ranges.
            result = table_extract(data, filename)
            result["filename"] = filename
            result["mode"] = "structured_table"
            return result
        else:
            # PDF: try smart table extraction first, fall back to text regex.
            table_result = table_extract(data, filename)
            if table_result["total_rows"] > 0:
                table_result["filename"] = filename
                table_result["mode"] = "structured_table"
                return table_result
            # Fall back to keyword/regex extraction.
            result = pdf_parser.parse(data, kind)
            result["filename"] = filename
            result["mode"] = "text_regex"
            return result

    except ImportError as exc:
        raise HTTPException(500, f"חסרה תלות: {exc}. הרץ pip install -r requirements.txt")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(422, f"לא ניתן לקרוא את הקובץ: {exc}")


@router.post("/analyze-table")
async def analyze_table(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    save: str = Form("false"),
    _account: User = Depends(current_user),
) -> dict:
    """Smart Excel/PDF analysis: extract → run ALL engines → return recommendations.

    If save=true, persists the rows to the user's lab history first, so trends,
    projections, and notifications include this upload's data permanently.
    Otherwise runs a transient analysis (preview without saving).
    """
    from app.auth import authorize_profile
    from app.db import SessionLocal
    from app.engines import report_engine
    from app.data.aliases import MARKER_ALIASES
    from app.data.lab_reference import marker_meta
    from app.data.units import normalize
    from app.models import LabResult

    db = SessionLocal()
    try:
        user = authorize_profile(_account, user_id, db)

        filename = file.filename or ""
        data = await file.read()
        if not data:
            raise HTTPException(400, "קובץ ריק.")

        # 1) Extract structured table from Excel/PDF
        table_result = table_extract(data, filename)
        rows = table_result["rows"]

        if not rows:
            return {
                "filename": filename,
                "total_rows": 0,
                "mapped": 0,
                "saved": False,
                "doc_flags": [],
                "recommendations": [],
                "matched_rows": [],
                "unmatched_rows": [],
                "warnings": table_result["warnings"] or [
                    "לא זוהתה טבלה. אם זה PDF סרוק — נדרש OCR (לא מותקן)."
                ],
            }

        # 2) Map each row to a canonical marker (if known)
        import datetime
        matched: list[dict] = []
        unmatched: list[dict] = []
        will_save = save.lower() == "true"

        for row in rows:
            name_lc = row["name"].lower()
            matched_key = None
            for key, aliases in MARKER_ALIASES.items():
                if any(a in name_lc for a in aliases):
                    matched_key = key
                    break

            row_out = {
                "original_name": row["name"],
                "marker": matched_key,
                "value": row["value"],
                "unit": row["unit"],
                "ref": f"{row['ref_low'] or ''}–{row['ref_high'] or ''}".strip("–"),
                "status": row["status"],
                "taken_on": row["taken_on"],
            }

            if matched_key:
                matched.append(row_out)
                if will_save:
                    # Normalize units to canonical before saving
                    canonical_value, _ = normalize(matched_key, row["value"], row["unit"] or "")
                    meta = marker_meta(matched_key)
                    try:
                        taken = datetime.date.fromisoformat(row["taken_on"])
                    except Exception:
                        taken = datetime.date.today()
                    db.add(LabResult(
                        user_id=user.id,
                        marker=matched_key,
                        value=canonical_value,
                        unit=(meta["unit"] if meta else (row["unit"] or "")),
                        taken_on=taken,
                    ))
            else:
                unmatched.append(row_out)

        if will_save:
            db.commit()
            db.refresh(user)  # reload relationships

        # 3) Document's own out-of-range flags (works for ALL rows, even unmatched)
        doc_flags = [
            {
                "name": r["original_name"],
                "value": r["value"],
                "unit": r["unit"],
                "status": r["status"],
                "ref": r["ref"],
                "matched": r["marker"] is not None,
            }
            for r in matched + unmatched
            if r["status"] in ("high", "low")
        ]

        # 4) Run the FULL report engine (all 18 engines: blood, drugs, family,
        #    insurance, screenings, projections, correlations, emergency, etc.)
        full_report = report_engine.generate(user)

        # 5) Surface the most actionable recommendations
        recommendations = (
            full_report.emergency_alerts
            + full_report.top_priorities
            + full_report.drug_interactions[:3]
            + full_report.missing_screenings[:3]
            + full_report.insurance_insights[:3]
        )
        # De-duplicate by title while preserving order
        seen: set[str] = set()
        unique_recs = []
        for f in recommendations:
            if f.title not in seen:
                seen.add(f.title)
                unique_recs.append(f.model_dump())

        return {
            "filename": filename,
            "total_rows": len(rows),
            "mapped": len(matched),
            "saved": will_save,
            "doc_flags": doc_flags,
            "matched_rows": matched,
            "unmatched_rows": unmatched,
            "health_score": full_report.health_score,
            "recommendations": unique_recs[:15],
            "warnings": table_result["warnings"],
        }
    finally:
        db.close()
