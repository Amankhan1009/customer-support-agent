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