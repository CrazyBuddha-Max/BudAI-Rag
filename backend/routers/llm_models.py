from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.llm_model import LLMModelService
from schemas.llm_model import LLMModelCreate, LLMModelUpdate, LLMModelResponse
from core.dependencies import get_admin_user, get_current_user

router = APIRouter(prefix="/api/v1/llm-models", tags=["大模型管理"])


# 管理员查看所有模型（包含is_active=false的）
@router.get("", response_model=list[LLMModelResponse])
async def list_models(
    admin=Depends(get_admin_user), db: AsyncSession = Depends(get_db)
):
    return await LLMModelService(db).get_all()


# 普通用户查看可用模型（只返回启用的）
@router.get("/active", response_model=list[LLMModelResponse])
async def list_active_models(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await LLMModelService(db).get_active()


# 管理员新增模型
@router.post("", response_model=LLMModelResponse, status_code=201)
async def create_model(
    data: LLMModelCreate,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await LLMModelService(db).create(data)


# 管理员更新模型
@router.patch("/{model_id}", response_model=LLMModelResponse)
async def update_model(
    model_id: str,
    data: LLMModelUpdate,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await LLMModelService(db).update(model_id, data)


# 管理员删除模型
@router.delete("/{model_id}")
async def delete_model(
    model_id: str, admin=Depends(get_admin_user), db: AsyncSession = Depends(get_db)
):
    return await LLMModelService(db).delete(model_id)
