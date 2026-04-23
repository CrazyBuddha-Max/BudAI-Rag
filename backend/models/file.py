import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    knowledge_base_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_bases.id"),
        nullable=True,  # 可以不属于任何知识库
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)  # 原始文件名
    stored_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # 存储时的文件名（防重名）
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # 服务器上的路径
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # 字节数
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf/txt/docx等
    parse_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",  # pending/parsing/done/failed
    )
    parse_error: Mapped[str] = mapped_column(Text, nullable=True)  # 解析失败的原因
