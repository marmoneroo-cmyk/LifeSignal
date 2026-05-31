"""Health goals router.

A goal is a user-set target for a marker (e.g. LDL below 100 by Dec 2026).
Progress is computed against the latest LabResult value at request time —
goals are not snapshots, they always reflect the current state.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import accessible_profile
from app.data.lab_reference import marker_meta
from app.db import get_db
from app.models import HealthGoal, LabResult, User

router = APIRouter(prefix="/api/users/{user_id}/goals", tags=["goals"])


class GoalIn(BaseModel):
    marker: str
    target_value: float
    direction: str = Field(pattern="^(below|above)$")
    deadline: date | None = None
    note: str = ""


class GoalOut(BaseModel):
    id: int
    marker: str
    label: str
    unit: str
    target_value: float
    direction: str
    deadline: date | None
    note: str
    latest_value: float | None
    latest_taken_on: date | None
    progress_pct: int   # 0-100 (100 = goal met)
    achieved: bool


def _latest(user: User, marker: str) -> LabResult | None:
    rows = [r for r in user.lab_results if r.marker == marker]
    return max(rows, key=lambda r: r.taken_on) if rows else None


def _progress(target: float, direction: str, latest: float, baseline: float | None) -> tuple[int, bool]:
    """Linear progress: 0 at baseline, 100 at/past target."""
    achieved = (direction == "below" and latest <= target) or (direction == "above" and latest >= target)
    if achieved:
        return 100, True
    if baseline is None or baseline == target:
        return 0, False
    pct = round((baseline - latest) / (baseline - target) * 100) if direction == "below" \
        else round((latest - baseline) / (target - baseline) * 100)
    return max(0, min(99, pct)), False


@router.post("", response_model=GoalOut, status_code=201)
def create_goal(
    payload: GoalIn,
    user: User = Depends(accessible_profile),
    db: Session = Depends(get_db),
) -> GoalOut:
    if marker_meta(payload.marker) is None:
        raise HTTPException(422, f"Unknown marker: {payload.marker}")
    row = HealthGoal(
        user_id=user.id,
        marker=payload.marker.lower(),
        target_value=payload.target_value,
        direction=payload.direction,
        deadline=payload.deadline,
        note=payload.note,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_out(row, user)


@router.get("", response_model=list[GoalOut])
def list_goals(
    user: User = Depends(accessible_profile),
    db: Session = Depends(get_db),
) -> list[GoalOut]:
    rows = db.scalars(
        select(HealthGoal).where(HealthGoal.user_id == user.id).order_by(HealthGoal.created_at.desc())
    )
    return [_to_out(r, user) for r in rows]


@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    user: User = Depends(accessible_profile),
    db: Session = Depends(get_db),
) -> None:
    row = db.scalar(select(HealthGoal).where(HealthGoal.id == goal_id, HealthGoal.user_id == user.id))
    if row:
        db.delete(row)
        db.commit()


def _to_out(g: HealthGoal, user: User) -> GoalOut:
    meta = marker_meta(g.marker) or {}
    latest_row = _latest(user, g.marker)

    # Baseline = first ever value for this marker (when the goal began making sense).
    rows = sorted([r for r in user.lab_results if r.marker == g.marker], key=lambda r: r.taken_on)
    baseline = rows[0].value if rows else None

    if latest_row:
        pct, achieved = _progress(g.target_value, g.direction, latest_row.value, baseline)
    else:
        pct, achieved = 0, False

    return GoalOut(
        id=g.id,
        marker=g.marker,
        label=meta.get("label", g.marker),
        unit=meta.get("unit", ""),
        target_value=g.target_value,
        direction=g.direction,
        deadline=g.deadline,
        note=g.note,
        latest_value=latest_row.value if latest_row else None,
        latest_taken_on=latest_row.taken_on if latest_row else None,
        progress_pct=pct,
        achieved=achieved,
    )
