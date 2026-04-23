from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.knowledge_base import KnowledgeBase
from typing import Optional


class KnowledgeBaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all_by_user(self, user_id: str) -> list[KnowledgeBase]:
        result = await self.db.execute(
            select(KnowledgeBase).where(KnowledgeBase.user_id == user_id)
        )
        return result.scalars().all()

    async def find_by_id(self, kb_id: str) -> Optional[KnowledgeBase]:
        result = await self.db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: str, data: dict) -> KnowledgeBase:
        kb = KnowledgeBase(user_id=user_id, **data)
        self.db.add(kb)
        await self.db.flush()
        await self.db.refresh(kb)
        return kb

    async def update(self, kb: KnowledgeBase, data: dict) -> KnowledgeBase:
        for field, value in data.items():
            setattr(kb, field, value)
        await self.db.flush()
        await self.db.refresh(kb)
        return kb

    async def delete(self, kb: KnowledgeBase) -> None:
        await self.db.delete(kb)
        await self.db.flush()
