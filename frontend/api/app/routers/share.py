"""Doctor share link router.

Lets a logged-in user mint a short-lived URL token that anyone can open to view
a read-only snapshot of the profile's health report — no account needed. The
public endpoint validates expiry and returns the same HealthReport shape the
authenticated /report endpoint returns.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import accessible_profile
from app.db import get_db
from app.engines import report_engine
from app.engines.translator import translate_report
from app.models import ShareToken, User
from app.schemas import HealthReport

router = APIRouter(tags=["share"])


class ShareIn(BaseModel):
    label: str = Field(default="", max_length=120)
    days_valid: int = Field(default=7, ge=1, le=30)


class ShareOut(BaseModel):
    token: str
    expires_at: datetime
    label: str


@router.post("/api/users/{user_id}/share", response_model=ShareOut, status_code=201)
def create_share(
    payload: ShareIn,
    user: User = Depends(accessible_profile),
    db: Session = Depends(get_db),
) -> ShareOut:
    token = secrets.token_urlsafe(32)  # 256 bits of entropy
    row = ShareToken(
        user_id=user.id,
        token=token,
        label=payload.label,
        expires_at=datetime.utcnow() + timedelta(days=payload.days_valid),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ShareOut(token=row.token, expires_at=row.expires_at, label=row.label)


@router.get("/api/users/{user_id}/share", response_model=list[ShareOut])
def list_shares(
    user: User = Depends(accessible_profile),
    db: Session = Depends(get_db),
) -> list[ShareOut]:
    rows = db.scalars(
        select(ShareToken)
        .where(ShareToken.user_id == user.id, ShareToken.expires_at > datetime.utcnow())
        .order_by(ShareToken.created_at.desc())
    )
    return [ShareOut(token=r.token, expires_at=r.expires_at, label=r.label) for r in rows]


@router.delete("/api/users/{user_id}/share/{token}", status_code=204)
def revoke_share(
    token: str,
    user: User = Depends(accessible_profile),
    db: Session = Depends(get_db),
) -> None:
    row = db.scalar(
        select(ShareToken).where(ShareToken.token == token, ShareToken.user_id == user.id)
    )
    if row:
        db.delete(row)
        db.commit()


# Public — NO auth required. Validates token and returns the report.
@router.get("/api/share/{token}", response_model=HealthReport)
def view_shared(
    token: str,
    lang: str = "he",
    db: Session = Depends(get_db),
) -> HealthReport:
    row = db.scalar(select(ShareToken).where(ShareToken.token == token))
    if not row:
        raise HTTPException(404, "קישור לא קיים או שפג תוקפו.")
    if row.expires_at < datetime.utcnow():
        raise HTTPException(410, "פג תוקף הקישור.")
    target = db.get(User, row.user_id)
    if not target:
        raise HTTPException(404, "הפרופיל לא קיים.")
    return translate_report(report_engine.generate(target), lang)
