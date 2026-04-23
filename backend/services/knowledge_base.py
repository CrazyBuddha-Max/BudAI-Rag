from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.knowledge_base import KnowledgeBaseRepository
from schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate


class KnowledgeBaseService:
    def __init__(self, db: AsyncSession):
        self.repo = KnowledgeBaseRepository(db)

    async def get_all(self, user_id: str):
        return await self.repo.find_all_by_user(user_id)

    async def get_by_id(self, kb_id: str, user_id: str):
        kb = await self.repo.find_by_id(kb_id)
        if not kb or kb.user_id != user_id:
            raise HTTPException(status_code=404, detail="知识库不存在")
        return kb

    async def create(self, user_id: str, data: KnowledgeBaseCreate):
        return await self.repo.create(user_id, data.model_dump())

    async def update(self, kb_id: str, user_id: str, data: KnowledgeBaseUpdate):
        kb = await self.get_by_id(kb_id, user_id)
        return await self.repo.update(kb, data.model_dump(exclude_none=True))

    async def delete(self, kb_id: str, user_id: str):
        kb = await self.get_by_id(kb_id, user_id)
        await self.repo.delete(kb)
        return {"message": f"知识库 {kb.name} 已删除"}
