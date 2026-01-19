from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class NotificationResponse(BaseModel):
    id: int
    type: str
    actor_username: str
    post_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    message: str

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
    total_pages: int
