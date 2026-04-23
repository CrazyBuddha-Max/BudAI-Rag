from pydantic import BaseModel, Field
from typing import Optional


class ConversationCreate(BaseModel):
    assistant_id: str
    title: str = Field("新对话", max_length=100)


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    assistant_id: str
    title: str

    model_config = {"from_attributes": True}


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
