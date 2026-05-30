"""Authentication + account/profile management (local JWT).

An *account* is a User row with an email + password. It can also own *dependent
profiles* (e.g. children) — User rows with no credentials and managed_by set to
the account. This delivers multi-user + family accounts without an external IdP.
"""
from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import create_token, current_user, hash_password, verify_password
from app.db import get_db
from app.models import User
from app.schemas import DependentIn, LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    email = payload.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email already registered")
    user = User(
        name=payload.name,
        sex=payload.sex,
        birth_date=payload.birth_date,
        smoker=payload.smoker,
        family_history=",".join(payload.family_history),
        region=payload.region,
        email=email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, int(time.time()))
    return TokenOut(token=token, user=UserOut.model_validate({**user.__dict__, "age": user.age}))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    token = create_token(user.id, int(time.time()))
    return TokenOut(token=token, user=UserOut.model_validate({**user.__dict__, "age": user.age}))


@router.get("/me", response_model=UserOut)
def me(account: User = Depends(current_user)) -> UserOut:
    return UserOut.model_validate({**account.__dict__, "age": account.age})


@router.get("/profiles", response_model=list[UserOut])
def list_profiles(account: User = Depends(current_user), db: Session = Depends(get_db)) -> list[UserOut]:
    rows = db.scalars(
        select(User).where((User.id == account.id) | (User.managed_by_user_id == account.id))
    )
    return [UserOut.model_validate({**u.__dict__, "age": u.age}) for u in rows]


@router.post("/profiles", response_model=UserOut, status_code=201)
def add_profile(
    payload: DependentIn,
    account: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    dependent = User(
        name=payload.name,
        sex=payload.sex,
        birth_date=payload.birth_date,
        smoker=payload.smoker,
        family_history=",".join(payload.family_history),
        region=payload.region,
        managed_by_user_id=account.id,
    )
    db.add(dependent)
    db.commit()
    db.refresh(dependent)
    return UserOut.model_validate({**dependent.__dict__, "age": dependent.age})
