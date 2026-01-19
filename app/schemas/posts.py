from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PostCreate(BaseModel):
    content: Optional[str] = None
    media_url: Optional[str] = None
    is_private: bool = False


class PostUpdate(BaseModel):
    content: Optional[str] = None
    media_url: Optional[str] = None
    is_private: Optional[bool] = None


class PostResponse(BaseModel):
    id: int
    content: Optional[str]
    media_url: Optional[str]
    is_private: bool
    likes_count: int
    created_at: datetime

    author_id: int

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
