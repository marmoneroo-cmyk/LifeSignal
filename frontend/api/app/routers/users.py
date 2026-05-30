"""User/profile read endpoints (auth-scoped).

Account creation happens via /api/auth/register; dependent profiles via
/api/auth/profiles. These endpoints expose only profiles the caller owns.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import accessible_profile, current_user
from app.data import sample_data
from app.db import get_db
from app.models import User
from app.schemas import UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_my_profiles(account: User = Depends(current_user), db: Session = Depends(get_db)) -> list[UserOut]:
    rows = db.scalars(
        select(User)
        .where((User.id == account.id) | (User.managed_by_user_id == account.id))
        .order_by(User.id)
    )
    return [UserOut.model_validate({**u.__dict__, "age": u.age}) for u in rows]


@router.get("/{user_id}", response_model=UserOut)
def get_user(user: User = Depends(accessible_profile)) -> UserOut:
    return UserOut.model_validate({**user.__dict__, "age": user.age})


@router.post("/{user_id}/load-sample")
def load_sample_data(
    user: User = Depends(accessible_profile),
    db: Session = Depends(get_db),
) -> dict:
    """Populate the active profile with realistic sample health data."""
    return {"added": sample_data.populate(db, user)}


@router.get("/{user_id}/has-data")
def has_data(user: User = Depends(accessible_profile)) -> dict:
    """Quick check the onboarding flow uses to know if a profile is empty."""
    return {
        "labs": len(user.lab_results) > 0,
        "policies": len(user.policies) > 0,
        "medications": len(user.medications) > 0,
        "family": len(user.family_members) > 0,
        "is_empty": not (user.lab_results or user.policies or user.medications or user.family_members),
    }
