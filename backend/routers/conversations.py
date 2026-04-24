from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.conversation import ConversationService
from services.ai.chat import ChatService
from schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
)
from schemas.message import ChatRequest, MessageResponse
from repositories.message import MessageRepository
from core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/conversations", tags=["对话管理"])


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await ConversationService(db).get_all(current_user.id)


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ConversationService(db).create(current_user.id, data)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ConversationService(db).update(conversation_id, current_user.id, data)


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ConversationService(db).delete(conversation_id, current_user.id)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取某个对话窗口的所有历史消息"""
    await ConversationService(db).get_by_id(conversation_id, current_user.id)
    return await MessageRepository(db).find_by_conversation(conversation_id)


@router.post("/chat")
async def chat(
    request: ChatRequest,
    stream: bool = Query(default=True, description="是否流式返回"),  # URL参数控制
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat_service = ChatService(db)

    if stream:
        # 流式返回
        async def generate():
            async for chunk in chat_service.stream_chat(
                conversation_id=request.conversation_id,
                user_message=request.content,
                user_id=current_user.id,
                knowledge_base_id=request.knowledge_base_id,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    else:
        # 非流式返回，直接返回完整 JSON
        return await chat_service.normal_chat(
            conversation_id=request.conversation_id,
            user_message=request.content,
            user_id=current_user.id,
            knowledge_base_id=request.knowledge_base_id,
        )
