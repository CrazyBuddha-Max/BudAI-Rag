import uuid
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class LLMModel(Base):
    __tablename__ = "llm_models"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_key: Mapped[str] = mapped_column(String(200), nullable=False)
    api_base_url: Mapped[str] = mapped_column(String(200), nullable=True)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    embedding_type: Mapped[str] = mapped_column(String(20), default="api")
    embedding_model_name: Mapped[str] = mapped_column(String(200), nullable=True)
