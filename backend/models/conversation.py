import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 属于哪个用户
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    # 属于哪个AI助手
    assistant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assistants.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), default="新对话")
