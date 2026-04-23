from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.conversation import Conversation
from typing import Optional


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all_by_user(self, user_id: str) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(Conversation.user_id == user_id)
        )
        return result.scalars().all()

    async def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: str, data: dict) -> Conversation:
        conversation = Conversation(user_id=user_id, **data)
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def update(self, conversation: Conversation, data: dict) -> Conversation:
        for field, value in data.items():
            setattr(conversation, field, value)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def delete(self, conversation: Conversation) -> None:
        await self.db.delete(conversation)
        await self.db.flush()
