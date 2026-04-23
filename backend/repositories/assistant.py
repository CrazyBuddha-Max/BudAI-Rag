from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.assistant import Assistant


class AssistantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all_by_user(self, user_id: str) -> list[Assistant]:
        result = await self.db.execute(
            select(Assistant).where(Assistant.user_id == user_id)
        )
        return result.scalars().all()

    async def find_by_id(self, assistant_id: str) -> Assistant | None:
        result = await self.db.execute(
            select(Assistant).where(Assistant.id == assistant_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: str, data: dict) -> Assistant:
        assistant = Assistant(user_id=user_id, **data)
        self.db.add(assistant)
        await self.db.flush()
        await self.db.refresh(assistant)
        return assistant

    async def update(self, assistant: Assistant, data: dict) -> Assistant:
        for field, value in data.items():
            setattr(assistant, field, value)
        await self.db.flush()
        await self.db.refresh(assistant)
        return assistant

    async def delete(self, assistant: Assistant) -> None:
        await self.db.delete(assistant)
        await self.db.flush()
