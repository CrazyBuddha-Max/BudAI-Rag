from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File as FastAPIFile,
    HTTPException,
)
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.file import FileService
from schemas.file import FileResponse, ParseRequest
from core.dependencies import get_current_user
from services.ai.embedding import EmbeddingService
from repositories.llm_model import LLMModelRepository
from repositories.file import FileRepository

router = APIRouter(prefix="/api/v1/files", tags=["文件管理"])


@router.get("", response_model=list[FileResponse])
async def list_files(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await FileService(db).get_all(current_user.id)


@router.post("", response_model=FileResponse, status_code=201)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user=Depends(get_current_user),  # 上传时不需要知识库id
    db: AsyncSession = Depends(get_db),
):
    return await FileService(db).upload(
        user_id=current_user.id,
        file=file,
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
        filename=file.filename,
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
    return await FileService(db).bind_knowledge_base(
        file_id, knowledge_base_id, current_user.id
    )


@router.post("/parse")
async def parse_files(
    request: ParseRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    批量解析文件并关联知识库
    支持单个或多个文件同时解析
    """
    model_repo = LLMModelRepository(db)
    embedding_model = await model_repo.find_by_id(request.embedding_model_id)
    if not embedding_model or not embedding_model.is_active:
        raise HTTPException(status_code=400, detail="Embedding模型不可用")

    file_repo = FileRepository(db)
    file_service = FileService(db)
    results = []

    for file_id in request.file_ids:
        file = await file_service.download(file_id, current_user.id)

        # 把文件关联到知识库
        await file_repo.update(
            file,
            {"knowledge_base_id": request.knowledge_base_id, "parse_status": "parsing"},
        )

        try:
            embedding_service = EmbeddingService()
            chunk_count = await embedding_service.parse_and_index(file, embedding_model)
            await embedding_service.close()
            await file_repo.update(file, {"parse_status": "done"})
            results.append(
                {
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "done",
                    "chunk_count": chunk_count,
                }
            )
        except Exception as e:
            await file_repo.update(
                file, {"parse_status": "failed", "parse_error": str(e)}
            )
            results.append(
                {
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e),
                }
            )

    return {"results": results}
