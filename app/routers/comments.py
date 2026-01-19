from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models import Post, User, Comment
from app.schemas import CommentResponse

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

    return new_comment


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

    return comment


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