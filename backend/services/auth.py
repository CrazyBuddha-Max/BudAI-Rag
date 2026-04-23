from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user import UserRepository
from core.security import hash_password, verify_password, create_access_token
from schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> dict:
        data.validate_passwords_match()
        if await self.repo.find_by_username(data.username):
            raise HTTPException(status_code=400, detail="用户名已存在")
        if await self.repo.find_by_email(data.email):
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        user = await self.repo.create(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return {"message": f"注册成功，欢迎 {user.username}"}

    async def login(self, username: str, password: str) -> dict:
        user = await self.repo.find_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="账号已被禁用")
        token = create_access_token(user_id=user.id, role=user.role)
        return {"access_token": token, "token_type": "bearer", "role": user.role}
