import os
import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.file import FileRepository
from repositories.knowledge_base import KnowledgeBaseRepository

# 文件存储目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许上传的文件类型
ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "txt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/markdown": "md",
}


class FileService:
    def __init__(self, db: AsyncSession):
        self.repo = FileRepository(db)
        self.kb_repo = KnowledgeBaseRepository(db)

    async def get_all(self, user_id: str):
        return await self.repo.find_all_by_user(user_id)

    async def get_by_kb(self, kb_id: str, user_id: str):
        # 先验证知识库属于当前用户
        kb = await self.kb_repo.find_by_id(kb_id)
        if not kb or kb.user_id != user_id:
            raise HTTPException(status_code=404, detail="知识库不存在")
        return await self.repo.find_by_kb(kb_id)

    async def upload(
        self, user_id: str, file: UploadFile, knowledge_base_id: str = None
    ):
        # 校验文件类型
        file_type = ALLOWED_TYPES.get(file.content_type)
        if not file_type:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型 {file.content_type}，支持：pdf/txt/docx/md",
            )

        # 如果指定了知识库，验证它属于当前用户
        if knowledge_base_id:
            kb = await self.kb_repo.find_by_id(knowledge_base_id)
            if not kb or kb.user_id != user_id:
                raise HTTPException(status_code=404, detail="知识库不存在")

        # 生成唯一文件名，防止重名覆盖
        stored_filename = f"{uuid.uuid4()}.{file_type}"
        file_path = os.path.join(UPLOAD_DIR, stored_filename)

        # 读取并保存文件到磁盘
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 保存文件记录到数据库
        return await self.repo.create(
            {
                "user_id": user_id,
                "knowledge_base_id": None,
                "filename": file.filename,
                "stored_filename": stored_filename,
                "file_path": file_path,
                "file_size": len(content),
                "file_type": file_type,
                "parse_status": "pending",
            }
        )

    async def download(self, file_id: str, user_id: str):
        file = await self.repo.find_by_id(file_id)
        if not file or file.user_id != user_id:
            raise HTTPException(status_code=404, detail="文件不存在")
        if not os.path.exists(file.file_path):
            raise HTTPException(status_code=404, detail="文件已丢失")
        return file

    async def delete(self, file_id: str, user_id: str):
        file = await self.repo.find_by_id(file_id)
        if not file or file.user_id != user_id:
            raise HTTPException(status_code=404, detail="文件不存在")
        # 删除磁盘文件
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        # 删除数据库记录
        await self.repo.delete(file)
        return {"message": f"文件 {file.filename} 已删除"}

    async def bind_knowledge_base(
        self, file_id: str, knowledge_base_id: str, user_id: str
    ):
        file = await self.repo.find_by_id(file_id)
        if not file or file.user_id != user_id:
            raise HTTPException(status_code=404, detail="文件不存在")

        kb = await self.kb_repo.find_by_id(knowledge_base_id)
        if not kb or kb.user_id != user_id:
            raise HTTPException(status_code=404, detail="知识库不存在")

        return await self.repo.update(file, {"knowledge_base_id": knowledge_base_id})
