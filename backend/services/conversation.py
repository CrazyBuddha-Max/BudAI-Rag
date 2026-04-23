from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.conversation import ConversationRepository
from repositories.assistant import AssistantRepository
from schemas.conversation import ConversationCreate, ConversationUpdate


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.repo = ConversationRepository(db)
        self.asst_repo = AssistantRepository(db)

    async def get_all(self, user_id: str):
        return await self.repo.find_all_by_user(user_id)

    async def get_by_id(self, conversation_id: str, user_id: str):
        conv = await self.repo.find_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            raise HTTPException(status_code=404, detail="对话窗口不存在")
        return conv

    async def create(self, user_id: str, data: ConversationCreate):
        # 验证助手属于当前用户
        assistant = await self.asst_repo.find_by_id(data.assistant_id)
        if not assistant or assistant.user_id != user_id:
            raise HTTPException(status_code=404, detail="助手不存在")
        return await self.repo.create(user_id, data.model_dump())

    async def update(
        self, conversation_id: str, user_id: str, data: ConversationUpdate
    ):
        conv = await self.get_by_id(conversation_id, user_id)
        return await self.repo.update(conv, data.model_dump(exclude_none=True))

    async def delete(self, conversation_id: str, user_id: str):
        conv = await self.get_by_id(conversation_id, user_id)
        await self.repo.delete(conv)
        return {"message": "对话窗口已删除"}
