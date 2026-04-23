from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.assistant import AssistantRepository
from repositories.llm_model import LLMModelRepository
from schemas.assistant import AssistantCreate, AssistantUpdate


class AssistantService:
    def __init__(self, db: AsyncSession):
        self.repo = AssistantRepository(db)
        self.model_repo = LLMModelRepository(db)

    async def get_all(self, user_id: str):
        return await self.repo.find_all_by_user(user_id)

    async def get_by_id(self, assistant_id: str, user_id: str):
        assistant = await self.repo.find_by_id(assistant_id)
        if not assistant or assistant.user_id != user_id:
            raise HTTPException(status_code=404, detail="助手不存在")
        return assistant

    async def create(self, user_id: str, data: AssistantCreate):
        # 验证模型存在且可用
        model = await self.model_repo.find_by_id(data.llm_model_id)
        if not model or not model.is_active:
            raise HTTPException(status_code=400, detail="所选大模型不可用")
        return await self.repo.create(user_id, data.model_dump())

    async def update(self, assistant_id: str, user_id: str, data: AssistantUpdate):
        assistant = await self.get_by_id(assistant_id, user_id)
        return await self.repo.update(assistant, data.model_dump(exclude_none=True))

    async def delete(self, assistant_id: str, user_id: str):
        assistant = await self.get_by_id(assistant_id, user_id)
        await self.repo.delete(assistant)
        return {"message": f"助手 {assistant.name} 已删除"}
