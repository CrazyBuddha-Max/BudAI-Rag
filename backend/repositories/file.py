from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.file import File
from typing import Optional


class FileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all_by_user(self, user_id: str) -> list[File]:
        result = await self.db.execute(select(File).where(File.user_id == user_id))
        return result.scalars().all()

    async def find_by_kb(self, kb_id: str) -> list[File]:
        result = await self.db.execute(
            select(File).where(File.knowledge_base_id == kb_id)
        )
        return result.scalars().all()

    async def find_by_id(self, file_id: str) -> Optional[File]:
        result = await self.db.execute(select(File).where(File.id == file_id))
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> File:
        file = File(**data)
        self.db.add(file)
        await self.db.flush()
        await self.db.refresh(file)
        return file

    async def update(self, file: File, data: dict) -> File:
        for field, value in data.items():
            setattr(file, field, value)
        await self.db.flush()
        await self.db.refresh(file)
        return file

    async def delete(self, file: File) -> None:
        await self.db.delete(file)
        await self.db.flush()
