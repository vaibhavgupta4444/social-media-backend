from sqlalchemy.orm import Session
from app.models import Notification, NotificationType, User, PushSubscription
import asyncio
import json
from datetime import datetime
from app.core.socketio_manager import send_notification_to_user, sio, is_user_connected
from app.core.config import settings
from app.database.connection import SessionLocal
from pywebpush import webpush, WebPushException
import threading


def generate_notification_message(notification_type: str, actor_username: str) -> str:
    """Generate a user-friendly notification message"""
    if notification_type == "follow":
        return f"{actor_username} started following you"
    elif notification_type == "like":
        return f"{actor_username} liked your post"
    elif notification_type == "comment":
        return f"{actor_username} commented on your post"
    return "New notification"


def send_web_push_to_user(user_id: int, notification_data: dict):
    """Send web push notifications to all stored endpoints for the user."""
    print(f"[WEB PUSH] Attempting to send web push to user {user_id}")
    
    if not settings.VAPID_PUBLIC_KEY or not settings.VAPID_PRIVATE_KEY:
        # Skip quietly if VAPID is not configured yet
        print("[WEB PUSH] ERROR: VAPID keys missing; skipping web push")
        return

    db = SessionLocal()
    try:
        subscriptions = db.query(PushSubscription).filter(
            PushSubscription.user_id == user_id
        ).all()

        print(f"[WEB PUSH] Found {len(subscriptions)} subscription(s) for user {user_id}")
        
        if not subscriptions:
            print(f"[WEB PUSH] No subscriptions found for user {user_id}")
            return

        payload = json.dumps({
            "title": "New notification",
            "body": notification_data.get("message", ""),
            "data": notification_data
        })

        for sub in subscriptions:
            try:
                print(f"[WEB PUSH] Sending to endpoint: {sub.endpoint[:50]}...")
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {
                            "p256dh": sub.p256dh,
                            "auth": sub.auth
                        }
                    },
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": settings.VAPID_SUBJECT}
                )
                print(f"[WEB PUSH] Successfully sent push notification to user {user_id}")
            except WebPushException as exc:
                # Remove stale subscriptions to keep the table clean
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                if status_code in (404, 410):
                    db.delete(sub)
                    db.commit()
                print(f"[WEB PUSH] ERROR: Web push send failed for user {user_id}: {exc}")
            except Exception as exc:
                print(f"[WEB PUSH] ERROR: Unexpected web push error for user {user_id}: {exc}")
    finally:
        db.close()


def schedule_web_push(user_id: int, notification_data: dict):
    """Run web push in a background thread so API handlers stay responsive."""
    print(f"[WEB PUSH] Scheduling web push for user {user_id}")
    threading.Thread(
        target=send_web_push_to_user,
        args=(user_id, notification_data),
        daemon=True
    ).start()


async def create_and_emit_notification(
    db: Session,
    user_id: int,
    actor_id: int,
    notification_type: NotificationType,
    post_id: int = None,
    comment_id: int = None
) -> Notification:
    """
    Create a notification in the database and emit it via Socket.IO
    
    Args:
        db: Database session
        user_id: ID of the user receiving the notification
        actor_id: ID of the user who triggered the notification
        notification_type: Type of notification (follow, like, comment)
        post_id: Optional post ID for like/comment notifications
        comment_id: Optional comment ID for comment notifications
    
    Returns:
        Created Notification object
    """
    # Create notification in database
    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type=notification_type,
        post_id=post_id,
        comment_id=comment_id
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Get actor information for the notification
    actor = db.query(User).filter(User.id == actor_id).first()
    
    if actor:
        # Prepare notification data for socket emission
        notification_data = {
            "id": notification.id,
            "type": notification_type.value,
            "actor_username": actor.username,
            "actor_id": actor.id,
            "post_id": post_id,
            "comment_id": comment_id,
            "is_read": False,
            "created_at": notification.created_at.isoformat(),
            "message": generate_notification_message(notification_type.value, actor.username)
        }
        
        # Emit notification via Socket.IO and fall back to web push if the user is offline
        try:
            asyncio.create_task(send_notification_to_user(user_id, notification_data))
            user_connected = is_user_connected(user_id)
            print(f"[NOTIFICATION] User {user_id} connected: {user_connected}")
            if not user_connected:
                print(f"[NOTIFICATION] User {user_id} is offline, triggering web push")
                schedule_web_push(user_id, notification_data)
            else:
                print(f"[NOTIFICATION] User {user_id} is online, skipping web push")
        except Exception as e:
            print(f"[NOTIFICATION] Error emitting socket notification: {e}")
    
    return notification



def create_and_emit_notification_sync(
    db: Session,
    user_id: int,
    actor_id: int,
    notification_type: NotificationType,
    post_id: int = None,
    comment_id: int = None
) -> Notification:
    """
    Synchronous wrapper for creating and emitting notifications
    Use this in synchronous route handlers
    """

    # Create notification in database
    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type=notification_type,
        post_id=post_id,
        comment_id=comment_id
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Get actor information
    actor = db.query(User).filter(User.id == actor_id).first()

    if not actor:
        return notification

    # Prepare notification payload
    notification_data = {
        "id": notification.id,
        "type": notification_type.value,
        "actor_username": actor.username,
        "actor_id": actor.id,
        "post_id": post_id,
        "comment_id": comment_id,
        "is_read": False,
        "created_at": notification.created_at.isoformat(),
        "message": generate_notification_message(
            notification_type.value,
            actor.username
        )
    }

    # ---- ASYNC SAFE EMISSION FROM SYNC CODE ----
    
    def emit_notification():
        asyncio.run(
            send_notification_to_user(user_id, notification_data)
        )

    try:
        threading.Thread(
            target=emit_notification,
            daemon=True
        ).start()
        user_connected = is_user_connected(user_id)
        print(f"[NOTIFICATION SYNC] User {user_id} connected: {user_connected}")
        if not user_connected:
            print(f"[NOTIFICATION SYNC] User {user_id} is offline, triggering web push")
            schedule_web_push(user_id, notification_data)
        else:
            print(f"[NOTIFICATION SYNC] User {user_id} is online, skipping web push")
    except Exception as e:
        # replace with proper logger in production
        print(f"[NOTIFICATION SYNC] Error emitting socket notification: {e}")

    return notification
