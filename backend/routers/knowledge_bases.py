from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.knowledge_base import KnowledgeBaseService
from schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
)
from schemas.file import FileResponse
from services.file import FileService
from core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/knowledge-bases", tags=["知识库管理"])


@router.get("", response_model=list[KnowledgeBaseResponse])
async def list_knowledge_bases(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await KnowledgeBaseService(db).get_all(current_user.id)


@router.post("", response_model=KnowledgeBaseResponse, status_code=201)
async def create_knowledge_base(
    data: KnowledgeBaseCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await KnowledgeBaseService(db).create(current_user.id, data)


@router.patch("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: str,
    data: KnowledgeBaseUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await KnowledgeBaseService(db).update(kb_id, current_user.id, data)


@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await KnowledgeBaseService(db).delete(kb_id, current_user.id)


@router.get("/{kb_id}/files", response_model=list[FileResponse])
async def list_kb_files(
    kb_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查看某个知识库下的所有文件"""
    return await FileService(db).get_by_kb(kb_id, current_user.id)
