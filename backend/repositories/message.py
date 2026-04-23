from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_conversation(self, conversation_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.id)  # 按插入顺序排
        )
        return result.scalars().all()

    async def create(
        self, conversation_id: str, role: str, content: str, token_count: int = 0
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message
