from pydantic import BaseModel
from typing import Optional


class FileResponse(BaseModel):
    id: str
    user_id: str
    knowledge_base_id: Optional[str]
    filename: str
    file_size: int
    file_type: str
    parse_status: str
    parse_error: Optional[str]

    model_config = {"from_attributes": True}


class ParseRequest(BaseModel):
    file_ids: list[str]  # 支持多个文件id
    knowledge_base_id: str  # 解析时才关联知识库
    embedding_model_id: str  # 用哪个模型做Embedding
