from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str  # 用户发的消息内容


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    token_count: int

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    conversation_id: str
    content: str  # 用户这次发的消息
