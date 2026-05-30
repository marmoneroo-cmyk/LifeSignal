"""Lab result intake (Blood Test Analyzer input).

The MVP accepts already-parsed marker/value pairs as JSON. A future OCR module
(Azure / Google Document AI) would feed this same endpoint after extraction.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import accessible_profile
from app.data.lab_reference import marker_meta
from app.data.units import normalize
from app.db import get_db
from app.models import LabResult, User
from app.schemas import LabBatchIn

router = APIRouter(prefix="/api/users/{user_id}/labs", tags=["labs"])


@router.post("", status_code=201)
def add_labs(
    user_id: int,
    payload: LabBatchIn,
    db: Session = Depends(get_db),
    _target: User = Depends(accessible_profile),
) -> dict:
    added, unknown, converted = 0, [], []
    for r in payload.results:
        meta = marker_meta(r.marker)
        if meta is None:
            unknown.append(r.marker)
            continue
        canonical_value, from_unit = normalize(r.marker, r.value, r.unit)
        if from_unit:
            converted.append(f"{r.marker}: {r.unit}→{meta['unit']}")
        db.add(
            LabResult(
                user_id=user_id,
                marker=r.marker.lower(),
                value=canonical_value,
                unit=meta["unit"],
                taken_on=r.taken_on,
            )
        )
        added += 1
    db.commit()
    return {"added": added, "unknown_markers": unknown, "converted_units": converted}
