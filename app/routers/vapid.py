from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.dependencies import get_db, get_verified_user
from app.models import PushSubscription, User

router = APIRouter(
    prefix="/vapid",
    tags=["notifications"]
)


@router.get("/public-key")
def get_vapid_public_key():
    """Get the VAPID public key for client-side service worker registration."""
    if not settings.VAPID_PUBLIC_KEY:
        return {
            "error": "VAPID not configured",
            "public_key": None
        }
    return {"public_key": settings.VAPID_PUBLIC_KEY}


@router.get("/debug")
def debug_vapid_config(
    db: Session = Depends(get_db),
    user: User = Depends(get_verified_user)
):
    """Debug endpoint to check VAPID configuration and user subscriptions"""
    
    # Check VAPID configuration
    vapid_configured = bool(settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY)
    
    # Get user's subscriptions
    subscriptions = db.query(PushSubscription).filter(
        PushSubscription.user_id == user.id
    ).all()
    
    return {
        "vapid_configured": vapid_configured,
        "vapid_public_key_set": bool(settings.VAPID_PUBLIC_KEY),
        "vapid_private_key_set": bool(settings.VAPID_PRIVATE_KEY),
        "vapid_subject": settings.VAPID_SUBJECT,
        "user_id": user.id,
        "subscription_count": len(subscriptions),
        "subscriptions": [
            {
                "id": sub.id,
                "endpoint": sub.endpoint[:50] + "..." if len(sub.endpoint) > 50 else sub.endpoint,
                "created_at": sub.created_at.isoformat()
            }
            for sub in subscriptions
        ]
    }
