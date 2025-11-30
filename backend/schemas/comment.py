from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    parent_id: Optional[int]
    created_at: datetime
    user_nickname: str
    children: List["CommentOut"] = []

    model_config = {"from_attributes": True}


CommentOut.model_rebuild()
