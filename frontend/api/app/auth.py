"""Local authentication: password hashing (pbkdf2, stdlib) + JWT (HS256).

Deliberately dependency-light and self-contained so the app runs without external
auth providers. For production, move JWT_SECRET to a real secret store and consider
a managed identity provider (Clerk/Auth0) — see README roadmap.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import User

_PBKDF2_ROUNDS = 200_000
_TOKEN_TTL_SECONDS = 7 * 24 * 3600


# ---- Password hashing -------------------------------------------------------

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        _, rounds_s, salt_hex, dk_hex = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds_s))
        return hmac.compare_digest(dk.hex(), dk_hex)
    except (ValueError, TypeError):
        return False


# ---- JWT (HS256) ------------------------------------------------------------

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def create_token(user_id: int, issued_at: int) -> str:
    """issued_at must be supplied by the caller (no clock calls here)."""
    secret = get_settings().jwt_secret.encode()
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64(json.dumps({"sub": user_id, "iat": issued_at, "exp": issued_at + _TOKEN_TTL_SECONDS}).encode())
    signing_input = f"{header}.{payload}".encode()
    sig = _b64(hmac.new(secret, signing_input, hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


def decode_token(token: str) -> int:
    secret = get_settings().jwt_secret.encode()
    try:
        header, payload, sig = token.split(".")
    except ValueError:
        raise HTTPException(401, "Malformed token")
    expected = _b64(hmac.new(secret, f"{header}.{payload}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(401, "Invalid token signature")
    data = json.loads(_b64decode(payload))
    if data.get("exp", 0) < int(time.time()):
        raise HTTPException(401, "Token expired")
    return int(data["sub"])


# ---- Dependencies -----------------------------------------------------------

def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    user_id = decode_token(authorization.split(" ", 1)[1])
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User no longer exists")
    return user


def authorize_profile(account: User, target_user_id: int, db: Session) -> User:
    """Allow access if target is the account itself or a profile it manages."""
    target = db.get(User, target_user_id)
    if not target:
        raise HTTPException(404, "Profile not found")
    if target.id != account.id and target.managed_by_user_id != account.id:
        raise HTTPException(403, "Not authorized for this profile")
    return target


def accessible_profile(
    user_id: int,
    account: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: resolve a path `user_id` the caller is allowed to access."""
    return authorize_profile(account, user_id, db)
