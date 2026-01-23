from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.follow import Follow
from app.models import User, Notification, NotificationType
from app.dependencies.auth import get_verified_user, get_db
from app.schemas import FollowerResponse, FollowerListResponse, FollowingResponse, FollowingListResponse
from typing import Annotated

router = APIRouter(prefix="/users", tags=["Follow"])

@router.post("/{user_id}/follow")
def follow_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: User = Depends(get_verified_user)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    user = db.query(User).filter(User.id == user_id, User.is_verified == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    already_following = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if already_following:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )

    follow = Follow(
        follower_id=current_user.id,
        following_id=user_id
    )

    db.add(follow)
    db.commit()

    # Create notification for the followed user and emit via Socket.IO
    from app.core.notification_helper import create_and_emit_notification_sync
    create_and_emit_notification_sync(
        db=db,
        user_id=user_id,
        actor_id=current_user.id,
        notification_type=NotificationType.FOLLOW
    )

    return {"message": "User followed successfully"}

@router.delete("/{user_id}/unfollow")
def unfollow_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: User = Depends(get_verified_user)
):
    target_user = db.query(User).filter(User.id == user_id, User.is_verified == True).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not following this user"
        )

    db.delete(follow)
    db.commit()

    return {"message": "User unfollowed successfully"}

@router.get("/{user_id}/followers", response_model=FollowerListResponse)
def get_followers(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.id == user_id, User.is_verified == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get followers with their usernames
    followers = (
        db.query(User)
        .join(Follow, Follow.follower_id == User.id)
        .filter(Follow.following_id == user_id)
        .all()
    )

    return FollowerListResponse(
        count=len(followers),
        followers=[FollowerResponse(username=follower.username) for follower in followers]
    )


@router.get("/{user_id}/following", response_model=FollowingListResponse)
def get_following(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.id == user_id, User.is_verified == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get following users with their usernames
    following = (
        db.query(User)
        .join(Follow, Follow.following_id == User.id)
        .filter(Follow.follower_id == user_id)
        .all()
    )

    return FollowingListResponse(
        count=len(following),
        following=[FollowingResponse(username=user.username) for user in following]
    )


