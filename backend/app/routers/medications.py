"""Medication intake (Drug Interaction Engine input)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import accessible_profile
from app.data.drug_interactions import DRUG_ALIASES
from app.db import get_db
from app.models import Medication, User
from app.schemas import MedicationBatchIn

router = APIRouter(prefix="/api/users/{user_id}/medications", tags=["medications"])


def _canonical(name: str) -> str | None:
    n = name.strip().lower()
    for key, aliases in DRUG_ALIASES.items():
        if n == key or any(a in n for a in aliases):
            return key
    return None


@router.post("", status_code=201)
def add_medications(
    user_id: int,
    payload: MedicationBatchIn,
    db: Session = Depends(get_db),
    _target: User = Depends(accessible_profile),
) -> dict:
    added, unknown = 0, []
    for m in payload.medications:
        key = _canonical(m.name)
        if key is None:
            unknown.append(m.name)
            continue
        db.add(Medication(user_id=user_id, name=key, dose=m.dose))
        added += 1
    db.commit()
    return {"added": added, "unrecognized": unknown}


@router.get("/known")
def known_drugs() -> list[dict]:
    return [{"key": k, "label": k.replace("_", " ").title()} for k in DRUG_ALIASES]
