"""Insurance policy intake (Insurance Analyzer input)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import accessible_profile
from app.data.insurance_reference import coverage_meta
from app.db import get_db
from app.models import InsurancePolicy, User
from app.schemas import PolicyBatchIn

router = APIRouter(prefix="/api/users/{user_id}/policies", tags=["insurance"])


@router.post("", status_code=201)
def add_policies(
    user_id: int,
    payload: PolicyBatchIn,
    db: Session = Depends(get_db),
    _target: User = Depends(accessible_profile),
) -> dict:
    added, unknown = 0, []
    for p in payload.policies:
        if coverage_meta(p.coverage_type) is None:
            unknown.append(p.coverage_type)
            continue
        db.add(
            InsurancePolicy(
                user_id=user_id,
                provider=p.provider,
                coverage_type=p.coverage_type.lower(),
                monthly_premium=p.monthly_premium,
                renewal_date=p.renewal_date,
                deductible=p.deductible,
                ceiling=p.ceiling,
                exclusions=p.exclusions,
            )
        )
        added += 1
    db.commit()
    return {"added": added, "unknown_coverage_types": unknown}
