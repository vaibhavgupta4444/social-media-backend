from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.models import Post, User
from app.schemas import PostResponse, PostListResponse, PostUpdate
from app.core import upload_to_cloudinary
from app.dependencies import get_current_user, get_db
from typing import Optional
import math

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.post("/", response_model=PostResponse)
async def create_post(
    content: str = Form(None),
    media: UploadFile = File(None),
    is_private: bool = Form(False),
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

    if not content and not media:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post must have either content or media"
        )
    
    media_url = None
    if media and media.filename:
        try:
            media_url = upload_to_cloudinary(media.file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload media: {str(e)}"
            )

    post = Post(
        user_id=int(current_user['sub']),
        content=content,
        media_url=media_url,
        is_private=is_private
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return PostResponse(
        id=post.id,
        content=post.content,
        media_url=post.media_url,
        is_private=post.is_private,
        likes_count=post.likes_count,
        created_at=post.created_at,
        author_id=post.user_id
    )


@router.get("/", response_model=PostListResponse)
def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = int(current_user['sub'])
    query = db.query(Post).filter(
        (Post.is_private == False) | (Post.user_id == user_id)
    )
    

    total = query.count()
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size
    posts = query.order_by(Post.created_at.desc()).offset(offset).limit(page_size).all()
    
    return PostListResponse(
        posts=[PostResponse(
            id=post.id,
            content=post.content,
            media_url=post.media_url,
            is_private=post.is_private,
            likes_count=post.likes_count,
            created_at=post.created_at,
            author_id=post.user_id
        ) for post in posts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    user_id = int(current_user['sub'])
    
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.is_private and post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this post"
        )
    
    return PostResponse(
        id=post.id,
        content=post.content,
        media_url=post.media_url,
        is_private=post.is_private,
        likes_count=post.likes_count,
        created_at=post.created_at,
        author_id=post.user_id
    )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    content: Optional[str] = Form(None),
    media: Optional[UploadFile] = File(None),
    is_private: Optional[bool] = Form(None),
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
    
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )
    

    if content is not None:
        post.content = content
    
    if media and media.filename:
        try:
            media_url = upload_to_cloudinary(media.file)
            post.media_url = media_url
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload media: {str(e)}"
            )
    
    if is_private is not None:
        post.is_private = is_private
    
    db.commit()
    db.refresh(post)
    
    return PostResponse(
        id=post.id,
        content=post.content,
        media_url=post.media_url,
        is_private=post.is_private,
        likes_count=post.likes_count,
        created_at=post.created_at,
        author_id=post.user_id
    )


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
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
    
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
  
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )
    
    db.delete(post)
    db.commit()
    
    return {
        "success": True,
        "message": "Post deleted successfully"
    }
