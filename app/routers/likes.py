from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import Post, Like, User, Notification, NotificationType
from app.dependencies import get_verified_user, get_db
from typing import Annotated


router = APIRouter(
    prefix="/posts",
    tags=["likes"]
)


@router.post("/{post_id}/like")
def like_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: User = Depends(get_verified_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == user.id
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already liked this post"
        )
    new_like = Like(post_id=post_id, user_id=user.id)
    post.likes_count += 1
    
    db.add(new_like)
    db.commit()
    db.refresh(post)
    
    # Create notification for post owner (only if not liking own post)
    if post.user_id != user.id:
        notification = Notification(
            user_id=post.user_id,
            actor_id=user.id,
            type=NotificationType.LIKE,
            post_id=post_id
        )
        db.add(notification)
        db.commit()
    
    return {
        "success": True,
        "message": "Post liked successfully",
        "likes_count": post.likes_count
    }


@router.delete("/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: User = Depends(get_verified_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == user.id
    ).first()
    
    if not existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You haven't liked this post"
        )

    post.likes_count = max(0, post.likes_count - 1)
    db.delete(existing_like)
    db.commit()
    db.refresh(post)
    
    return {
        "success": True,
        "message": "Post unliked successfully",
        "likes_count": post.likes_count
    }