from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import UserCreate, UserResponse, ChangePassword, VerifyOTP, ForgotPassword, ResetPassword
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, get_verified_user
from app.models import User, Post, Follow
from app.core import (
    get_password_hash, 
    verify_password, 
    create_tokens, 
    send_otp_email,
    generate_otp,
    create_password_reset_token,
    verify_password_reset_token,
    send_password_reset_email
)
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime, timedelta, timezone

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me")
def get_user(
    db: Annotated[Session, Depends(get_db)],
    user: User = Depends(get_verified_user)):
    
    # Get posts count
    posts_count = db.query(Post).filter(Post.user_id == user.id).count()
    
    # Get followers list
    followers = db.query(Follow).filter(Follow.following_id == user.id).all()
    followers_list = [
        {
            "id": follower.follower_id,
            "username": db.query(User).filter(User.id == follower.follower_id).first().username
        }
        for follower in followers
    ]
    
    # Get following list
    following = db.query(Follow).filter(Follow.follower_id == user.id).all()
    following_list = [
        {
            "id": follow.following_id,
            "username": db.query(User).filter(User.id == follow.following_id).first().username
        }
        for follow in following
    ]
    
    return {
        "success": True,
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "posts_count": posts_count,
        "followers": followers_list,
        "following": following_list
    }

@router.post("/register")
def create_user(user: UserCreate,
                db:Annotated[Session ,Depends(get_db)]):
    is_user_exist = db.query(User).filter(User.email == user.email).first()

    if is_user_exist and is_user_exist.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User already exists and is verified")
    
    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    if not is_user_exist:
        # Create new user
        hashed_password = get_password_hash(user.password)
        user_data = user.model_dump()
        user_data.pop("password")    
        new_user = User(**user_data, hashed_password = hashed_password,
                        otp = otp, expires_at = expires_at, is_used = False)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    else:
        is_user_exist.username = user.username
        is_user_exist.hashed_password = get_password_hash(user.password)
        is_user_exist.otp = otp
        is_user_exist.expires_at = expires_at
        is_user_exist.is_used = False
        db.commit()
        db.refresh(is_user_exist)

    send_otp_email(user.email, otp)
    return {
        "success": True,
        "message": "OTP sent to your email"
    }

@router.post("/login", response_model=UserResponse)
def login(form_data: Annotated[OAuth2PasswordRequestForm , Depends()], 
          db: Annotated[Session, Depends(get_db)]):

    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not exists")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Please verify your email first")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect password")

    tokens = create_tokens(data={"sub": str(user.id)})
    return {"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]}


@router.get("/refresh", response_model= UserResponse)
def get_access_token(
    db: Annotated[Session, Depends(get_db)],
    user: User = Depends(get_verified_user)
):
    tokens = create_tokens(data={"sub": str(user.id)})
    return {"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]}


@router.post("/change-password")
def change_password(
    data: ChangePassword,
    db: Annotated[Session, Depends(get_db)],
    user: User = Depends(get_verified_user)
):
    if not verify_password(hashed_password=user.hashed_password,plain_password= data.current_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Password")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "Password Changed Successfully"}


@router.post("/verify-otp", response_model=UserResponse)
def verify_otp(
    data: VerifyOTP,
    db: Annotated[Session, Depends(get_db)]
):
    user = db.query(User).filter(
        User.email == data.email,
        User.otp == data.otp,
        User.is_used == False
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP or OTP already used"
        )

  
    if user.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )

    user.is_used = True
    user.is_verified = True
    user.otp = None
    db.commit()
    db.refresh(user)

    
    tokens = create_tokens(data={"sub": str(user.id)})
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    }


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPassword,
    db: Annotated[Session, Depends(get_db)]
):

    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    reset_token = create_password_reset_token(user.email)

    send_password_reset_email(user.email, reset_token)
    
    return {
        "success": True,
        "message": "Password reset link sent to your email"
    }


@router.post("/reset-password")
def reset_password(
    data: ResetPassword,
    db: Annotated[Session, Depends(get_db)]
):
   
    email = verify_password_reset_token(data.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "message": "Password reset successfully"
    }