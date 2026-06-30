from fastapi import APIRouter, Depends, HTTPException

from chatbot.application.use_cases.chat_orchestrator import ChatOrchestrator
from chatbot.infrastructure.di import get_chat_orchestrator
from chatbot.infrastructure.http.dtos.chat_dto import ChatRequestDto, ChatResponseDto
from shared.infrastructure.di import jwt_auth_guard
from users.domain.user import User


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat(
    body: ChatRequestDto,
    user: User = Depends(jwt_auth_guard),
    orchestrator: ChatOrchestrator = Depends(get_chat_orchestrator),
):
    try:
        result = await orchestrator.process_user_message(
            user_id=user.id,
            user_input=body.user_input,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return ChatResponseDto(response=result)



