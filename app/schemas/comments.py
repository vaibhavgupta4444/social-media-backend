from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CommentResponse(BaseModel):
    id: int
    post_id: int
    username: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
