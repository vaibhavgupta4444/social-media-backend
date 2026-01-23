from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas import Subscription
from app.dependencies import get_db, get_verified_user
from app.models import PushSubscription, User
from app.core.notification_helper import send_web_push_to_user


router = APIRouter(
    prefix="/push-subscriptions",
    tags=["notifications"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def save_subscription(
    sub: Subscription,
    db: Session = Depends(get_db),
    user: User = Depends(get_verified_user)
):
    # Upsert the subscription so re-registering on the client simply refreshes the keys
    existing = db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id,
        PushSubscription.endpoint == str(sub.endpoint)
    ).first()

    if existing:
        existing.p256dh = sub.keys.p256dh
        existing.auth = sub.keys.auth
        db.commit()
        db.refresh(existing)
        return {"message": "Subscription updated"}

    new_subscription = PushSubscription(
        user_id=user.id,
        endpoint=str(sub.endpoint),
        p256dh=sub.keys.p256dh,
        auth=sub.keys.auth
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return {"message": "Subscribed"}


@router.delete("/")
def delete_subscription(
    sub: Subscription,
    db: Session = Depends(get_db),
    user: User = Depends(get_verified_user)
):
    record = db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id,
        PushSubscription.endpoint == str(sub.endpoint)
    ).first()

    if record:
        db.delete(record)
        db.commit()
        return {"message": "Subscription deleted"}

    return {"message": "No subscription found"}


@router.post("/test", status_code=status.HTTP_200_OK)
def test_push_notification(
    db: Session = Depends(get_db),
    user: User = Depends(get_verified_user)
):
    """Test endpoint to manually send a push notification to the current user"""
    
    # Check if user has subscriptions
    subscription_count = db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id
    ).count()
    
    if subscription_count == 0:
        return {
            "success": False,
            "message": "No push subscriptions found for your account"
        }
    
    # Prepare test notification data
    test_notification = {
        "id": 999,
        "type": "test",
        "actor_username": "System",
        "actor_id": 0,
        "post_id": None,
        "comment_id": None,
        "is_read": False,
        "created_at": "2026-01-23T00:00:00",
        "message": "This is a test push notification!"
    }
    
    # Send the push notification directly (synchronously for testing)
    try:
        send_web_push_to_user(user.id, test_notification)
        return {
            "success": True,
            "message": f"Test push notification sent to {subscription_count} subscription(s)",
            "user_id": user.id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send push notification: {str(e)}"
        }