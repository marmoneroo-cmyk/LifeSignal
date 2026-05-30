"""Family member intake (Family Health Graph input)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import accessible_profile
from app.db import get_db
from app.models import FamilyMember, User
from app.schemas import FamilyBatchIn

router = APIRouter(prefix="/api/users/{user_id}/family", tags=["family"])

KNOWN_CONDITIONS = [
    "heart_disease",
    "diabetes",
    "breast_cancer",
    "ovarian_cancer",
    "colon_cancer",
    "prostate_cancer",
    "melanoma",
]
RELATIONS = ["father", "mother", "sibling", "grandparent", "child", "aunt", "uncle"]


@router.post("", status_code=201)
def add_family(
    user_id: int,
    payload: FamilyBatchIn,
    db: Session = Depends(get_db),
    _target: User = Depends(accessible_profile),
) -> dict:
    for m in payload.members:
        db.add(
            FamilyMember(
                user_id=user_id,
                relation=m.relation.strip().lower(),
                conditions=",".join(c.strip().lower() for c in m.conditions),
            )
        )
    db.commit()
    return {"added": len(payload.members)}


@router.get("/reference")
def reference() -> dict:
    return {"relations": RELATIONS, "conditions": KNOWN_CONDITIONS}
