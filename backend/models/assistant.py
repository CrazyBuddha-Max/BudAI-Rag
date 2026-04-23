import uuid
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Assistant(Base):
    __tablename__ = "assistants"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 属于哪个用户
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    # 使用哪个大模型
    llm_model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("llm_models.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(
        String(2000), default="你是一个有帮助的AI助手"
    )
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    context_length: Mapped[int] = mapped_column(
        Integer, default=4000
    )  # 上下文token限制
    top_n: Mapped[int] = mapped_column(Integer, default=3)  # RAG召回数量
