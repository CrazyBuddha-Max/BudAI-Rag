from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.llm_model import LLMModel
from typing import Optional


class LLMModelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all(self) -> list[LLMModel]:
        result = await self.db.execute(select(LLMModel))
        return result.scalars().all()

    async def find_by_id(self, model_id: str) -> Optional[LLMModel]:
        result = await self.db.execute(select(LLMModel).where(LLMModel.id == model_id))
        return result.scalar_one_or_none()

    async def find_active(self) -> list[LLMModel]:
        """只返回启用的模型，给AI对话用"""
        result = await self.db.execute(select(LLMModel).where(LLMModel.is_active))
        return result.scalars().all()

    async def create(self, data: dict) -> LLMModel:
        model = LLMModel(**data)
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return model

    async def update(self, model: LLMModel, data: dict) -> LLMModel:
        for field, value in data.items():
            setattr(model, field, value)
        await self.db.flush()
        await self.db.refresh(model)
        return model

    async def delete(self, model: LLMModel) -> None:
        await self.db.delete(model)
        await self.db.flush()
