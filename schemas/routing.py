from typing import Literal

from pydantic import BaseModel, Field


class IntentClassification(BaseModel):
    intent: Literal[
        "billing",
        "technical",
        "account",
        "general",
        "unknown",
    ] = Field(
        description="The customer support intent detected from the message."
    )