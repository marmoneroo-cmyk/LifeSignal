"""Auth primitives: password hashing and JWT round-trip."""
from __future__ import annotations

import time

import pytest
from fastapi import HTTPException

from app.auth import create_token, decode_token, hash_password, verify_password


def test_password_hash_roundtrip():
    h = hash_password("demo1234")
    assert h != "demo1234"  # never store plaintext
    assert verify_password("demo1234", h)
    assert not verify_password("wrong", h)


def test_verify_handles_missing_hash():
    assert not verify_password("anything", None)
    assert not verify_password("anything", "garbage")


def test_jwt_roundtrip():
    token = create_token(user_id=42, issued_at=int(time.time()))
    assert decode_token(token) == 42


def test_jwt_rejects_tampering():
    token = create_token(user_id=7, issued_at=int(time.time()))
    tampered = token[:-3] + ("aaa" if not token.endswith("aaa") else "bbb")
    with pytest.raises(HTTPException):
        decode_token(tampered)


def test_jwt_rejects_expired():
    token = create_token(user_id=7, issued_at=1)  # issued in 1970 -> long expired
    with pytest.raises(HTTPException):
        decode_token(token)
