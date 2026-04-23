from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user import UserRepository
from schemas.user import UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_all(self):
        return await self.repo.find_all()

    async def get_by_id(self, user_id: str):
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user

    async def update(self, user_id: str, data: UserUpdate):
        user = await self.get_by_id(user_id)
        update_data = data.model_dump(exclude_none=True)
        return await self.repo.update(user, update_data)

    async def delete(self, user_id: str):
        user = await self.get_by_id(user_id)
        await self.repo.delete(user)
        return {"message": f"用户 {user.username} 已删除"}
