"""Admin dashboard — aggregate stats for the logged-in account.

This is a per-account dashboard, NOT a global admin (which would need a real
role system). It surfaces totals across the account's own profiles: how many
lab results, policies, medications, shared links, goals, etc.

Useful for: confirming an upload took effect, seeing the data footprint of a
family group, and quick troubleshooting.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import current_user
from app.db import get_db
from app.models import (
    FamilyMember, HealthGoal, InsurancePolicy, LabResult,
    Medication, ShareToken, User,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _profile_ids(db: Session, account: User) -> list[int]:
    """The set of profile IDs this account has access to."""
    rows = db.scalars(
        select(User.id).where(
            (User.id == account.id) | (User.managed_by_user_id == account.id)
        )
    )
    return list(rows)


def _count(db: Session, model, profile_ids: list[int]) -> int:
    stmt = select(func.count()).select_from(model).where(model.user_id.in_(profile_ids))
    return int(db.scalar(stmt) or 0)


@router.get("/stats")
def stats(
    account: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return aggregate counts + most-recent activity for this account."""
    profile_ids = _profile_ids(db, account)

    # Active (non-expired) shares
    active_shares = int(db.scalar(
        select(func.count()).select_from(ShareToken).where(
            ShareToken.user_id.in_(profile_ids),
            ShareToken.expires_at > datetime.utcnow(),
        )
    ) or 0)

    # Most recent lab across all owned profiles, useful as a freshness indicator.
    latest_lab = db.scalar(
        select(LabResult).where(LabResult.user_id.in_(profile_ids))
        .order_by(LabResult.taken_on.desc()).limit(1)
    )

    return {
        "profiles": len(profile_ids),
        "labs": _count(db, LabResult, profile_ids),
        "policies": _count(db, InsurancePolicy, profile_ids),
        "medications": _count(db, Medication, profile_ids),
        "family_members": _count(db, FamilyMember, profile_ids),
        "goals": _count(db, HealthGoal, profile_ids),
        "active_shares": active_shares,
        "latest_lab": (
            {"marker": latest_lab.marker, "value": latest_lab.value,
             "unit": latest_lab.unit, "taken_on": latest_lab.taken_on.isoformat()}
            if latest_lab else None
        ),
    }
