from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.llm_model import LLMModelRepository
from schemas.llm_model import LLMModelCreate, LLMModelUpdate


class LLMModelService:
    def __init__(self, db: AsyncSession):
        self.repo = LLMModelRepository(db)

    async def get_all(self):
        return await self.repo.find_all()

    async def get_active(self):
        """给前端AI对话选模型用，只返回启用的"""
        return await self.repo.find_active()

    async def get_by_id(self, model_id: str):
        model = await self.repo.find_by_id(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
        return model

    async def create(self, data: LLMModelCreate):
        return await self.repo.create(data.model_dump())

    async def update(self, model_id: str, data: LLMModelUpdate):
        model = await self.get_by_id(model_id)
        update_data = data.model_dump(exclude_none=True)
        return await self.repo.update(model, update_data)

    async def delete(self, model_id: str):
        model = await self.get_by_id(model_id)
        await self.repo.delete(model)
        return {"message": f"模型 {model.name} 已删除"}
