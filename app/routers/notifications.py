from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.models import Notification, NotificationType, User
from app.schemas import NotificationResponse, NotificationListResponse
from app.dependencies import get_current_user, get_db
from typing import Annotated
import math


router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


def generate_notification_message(notification_type: str, actor_username: str) -> str:
    if notification_type == "follow":
        return f"{actor_username} started following you"
    elif notification_type == "like":
        return f"{actor_username} liked your post"
    elif notification_type == "comment":
        return f"{actor_username} commented on your post"
    return "New notification"


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = int(current_user['sub'])
    
    # Check if user exists and is verified
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    query = db.query(Notification, User).join(
        User, Notification.actor_id == User.id
    ).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    total = query.count()

    unread_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()
    
    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    results = query.order_by(
        Notification.created_at.desc()
    ).offset(offset).limit(page_size).all()
   
    notifications = []
    for notification, actor in results:
        notifications.append(NotificationResponse(
            id=notification.id,
            type=notification.type.value,
            actor_username=actor.username,
            post_id=notification.post_id,
            is_read=notification.is_read,
            created_at=notification.created_at,
            message=generate_notification_message(notification.type.value, actor.username)
        ))
    
    return NotificationListResponse(
        notifications=notifications,
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = int(current_user['sub'])
    
    # Check if user exists and is verified
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    
    return {"success": True, "message": "Notification marked as read"}


@router.put("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = int(current_user['sub'])
    
    # Check if user exists and is verified
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"success": True, "message": "All notifications marked as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = int(current_user['sub'])
    
    # Check if user exists and is verified
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    
    return {"success": True, "message": "Notification deleted"}
