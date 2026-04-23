from pydantic import BaseModel, Field
from typing import Optional


class LLMModelCreate(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, description="模型别名，自己取的名字"
    )
    provider: str = Field(..., description="提供商：openai/anthropic/zhipu/qwen")
    model_name: str = Field(..., description="模型名称：gpt-4o/claude-sonnet-4-5等")
    api_key: str = Field(..., description="API Key")
    api_base_url: Optional[str] = Field(
        None, description="自定义API地址，默认用官方地址"
    )
    max_tokens: int = Field(4096, ge=1, le=128000)


class LLMModelResponse(BaseModel):
    id: str
    name: str
    provider: str
    model_name: str
    api_base_url: Optional[str]
    max_tokens: int
    is_active: bool
    # 注意：api_key 不返回给前端

    model_config = {"from_attributes": True}


class LLMModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    is_active: Optional[bool] = None
