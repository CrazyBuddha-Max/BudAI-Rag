from pydantic import BaseModel, Field
from typing import Optional


class LLMModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="模型别名")
    provider: str = Field(..., description="openai/anthropic/deepseek等")
    model_name: str = Field(..., description="对话模型名称")
    api_key: str
    api_base_url: Optional[str] = None
    max_tokens: int = Field(4096, ge=1, le=128000)
    embedding_type: str = Field("api", description="api 或 local")
    embedding_model_name: Optional[str] = Field(
        None,
        description="api模式填 text-embedding-3-small，local模式填 BAAI/bge-small-zh-v1.5",
    )


class LLMModelResponse(BaseModel):
    id: str
    name: str
    provider: str
    model_name: str
    api_base_url: Optional[str]
    max_tokens: int
    is_active: bool
    embedding_type: str
    embedding_model_name: Optional[str]

    model_config = {"from_attributes": True}


class LLMModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    is_active: Optional[bool] = None
    embedding_type: Optional[str] = None
    embedding_model_name: Optional[str] = None
