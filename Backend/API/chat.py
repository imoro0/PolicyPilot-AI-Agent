
from fastapi import APIRouter

from Backend.Schemas.chat import ChatRequest, ChatResponse
from Backend.Services.chat_service import chat_with_policy_agent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = chat_with_policy_agent(
        question=request.question,
        session_id=request.session_id
    )

    return ChatResponse(answer=answer)
