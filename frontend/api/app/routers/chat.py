"""Chat with your data — RAG-style Q&A grounded in the user's profile."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth import accessible_profile
from app.engines import chat_engine
from app.models import User

router = APIRouter(prefix="/api/users/{user_id}/chat", tags=["chat"])


class ChatIn(BaseModel):
    question: str = Field(min_length=1, max_length=1500)


class ChatOut(BaseModel):
    answer: str
    generated_by: str
    model: str | None = None
    disclaimer: str


@router.post("", response_model=ChatOut)
def ask(payload: ChatIn, user: User = Depends(accessible_profile)) -> ChatOut:
    return ChatOut(**chat_engine.ask(user, payload.question))
