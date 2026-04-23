from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.assistant import AssistantService
from schemas.assistant import AssistantCreate, AssistantUpdate, AssistantResponse
from core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/assistants", tags=["AI助手管理"])


@router.get("", response_model=list[AssistantResponse])
async def list_assistants(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await AssistantService(db).get_all(current_user.id)


@router.post("", response_model=AssistantResponse, status_code=201)
async def create_assistant(
    data: AssistantCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await AssistantService(db).create(current_user.id, data)


@router.patch("/{assistant_id}", response_model=AssistantResponse)
async def update_assistant(
    assistant_id: str,
    data: AssistantUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await AssistantService(db).update(assistant_id, current_user.id, data)


@router.delete("/{assistant_id}")
async def delete_assistant(
    assistant_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await AssistantService(db).delete(assistant_id, current_user.id)
