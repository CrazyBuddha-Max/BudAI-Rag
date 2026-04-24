from pydantic import BaseModel, Field
from typing import Optional


class AssistantCreate(BaseModel):
    llm_model_id: str
    embedding_model_id: Optional[str] = None  # 不填就用对话模型的配置
    name: str = Field(..., min_length=1, max_length=100)
    system_prompt: str = Field("你是一个有帮助的AI助手", max_length=2000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(2048, ge=1, le=128000)
    context_length: int = Field(4000, ge=1, le=128000)
    top_n: int = Field(3, ge=1, le=20)


class AssistantResponse(BaseModel):
    id: str
    user_id: str
    llm_model_id: str
    embedding_model_id: Optional[str]
    name: str
    system_prompt: str
    temperature: float
    max_tokens: int
    context_length: int
    top_n: int

    model_config = {"from_attributes": True}


class AssistantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    system_prompt: Optional[str] = Field(None, max_length=2000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    context_length: Optional[int] = Field(None, ge=1, le=128000)
    top_n: Optional[int] = Field(None, ge=1, le=20)
    llm_model_id: Optional[str] = None
    embedding_model_id: Optional[str] = None
