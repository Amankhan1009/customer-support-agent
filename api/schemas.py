from typing import Any, Literal

from pydantic import BaseModel, Field


class SupportRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ResumeRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    human_response: str = Field(min_length=1)


class SupportResponse(BaseModel):
    thread_id: str
    status: Literal["completed", "human_review_required"]
    response: str | None = None
    interrupt_data: dict[str, Any] | None = None


class MessageHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ThreadHistoryResponse(BaseModel):
    thread_id: str
    messages: list[MessageHistoryItem] = []
    waiting_for_human: bool = False
    interrupt_data: dict[str, Any] | None = None


class UserThreadItem(BaseModel):
    thread_id: str
    title: str
    updated_at: str | None = None


# ── Auth schemas ──────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    username: str