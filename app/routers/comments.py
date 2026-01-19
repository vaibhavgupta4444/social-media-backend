from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models import Post, User, Comment, Notification, NotificationType
from app.schemas import CommentResponse, CommentListResponse
import math

router = APIRouter(
    prefix="/posts",
    tags=["comment"]
)

@router.post("/{post_id}/comment", response_model=CommentResponse)
def create_comment(
    post_id: str,
    content: str,
    db: Annotated[Session, Depends(get_db)],
    current_user = Depends(get_current_user)
):
    user_id = int(current_user['sub'])

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    new_comment = Comment(post_id = post_id, user_id = user_id, content = content)

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # Create notification for post owner (only if not commenting on own post)
    if post.user_id != user_id:
        notification = Notification(
            user_id=post.user_id,
            actor_id=user_id,
            type=NotificationType.COMMENT,
            post_id=post_id,
            comment_id=new_comment.id
        )
        db.add(notification)
        db.commit()

    return CommentResponse(
        id=new_comment.id,
        post_id=new_comment.post_id,
        username=user.username,
        content=new_comment.content,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at
    )

@router.get("/{post_id}/comment", response_model=CommentListResponse)
def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    total = db.query(Comment).filter(Comment.post_id == post_id).count()
    offset = (page - 1) * page_size
    results = (
        db.query(Comment, User)
        .join(User, Comment.user_id == User.id)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return CommentListResponse(
        comments=[CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            username=user.username,
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        ) for comment, user in results],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.put("/{post_id}/comment/{id}", response_model=CommentResponse)
def update_comment(
    id: str,
    post_id: str,
    content: str,
    db: Annotated[Session, Depends(get_db)],
    current_user = Depends(get_current_user)
):
    user_id = int(current_user['sub'])

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    comment = db.query(Comment).filter(
        Comment.id == id,
        Comment.post_id == post_id,
        Comment.user_id == user_id
    ).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    comment.content = content
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        username=user.username,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@router.delete("/{post_id}/comment/{id}")
def delete_comment(
    id: int,
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user = Depends(get_current_user)
):
    user_id = int(current_user['sub'])

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    comment = db.query(Comment).filter(
        Comment.id == id,
        Comment.post_id == post_id,
        Comment.user_id == user_id
    ).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return {
        "success": True,
        "message": "Comment deleted",
    }