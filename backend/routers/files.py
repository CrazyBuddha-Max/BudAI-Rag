from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, Form  # 加 Form
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database import get_db
from services.file import FileService
from schemas.file import FileResponse
from core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/files", tags=["文件管理"])


@router.get("", response_model=list[FileResponse])
async def list_files(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await FileService(db).get_all(current_user.id)


@router.post("", response_model=FileResponse, status_code=201)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    knowledge_base_id: Optional[str] = Form(None),  # 改这里，用 Form 接收
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FileService(db).upload(
        user_id=current_user.id, file=file, knowledge_base_id=knowledge_base_id
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file = await FileService(db).download(file_id, current_user.id)
    return FastAPIFileResponse(
        path=file.file_path,
        filename=file.filename,  # 下载时用原始文件名
        media_type="application/octet-stream",
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FileService(db).delete(file_id, current_user.id)


@router.patch("/{file_id}/bind-kb")
async def bind_to_knowledge_base(
    file_id: str,
    knowledge_base_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """把已上传的文件关联到指定知识库"""
    return await FileService(db).bind_knowledge_base(
        file_id, knowledge_base_id, current_user.id
    )
