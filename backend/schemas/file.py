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
