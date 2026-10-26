
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="The user's policy-related question"
    )

    session_id: str = Field(
        default="default",
        min_length=1,
        description="Identifier for the conversation session"
    )


class ChatResponse(BaseModel):
    answer: str
