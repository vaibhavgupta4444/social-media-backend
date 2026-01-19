from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import UserCreate, UserResponse, ChangePassword
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models import User
from app.core import get_password_hash, verify_password, create_tokens
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register")
def create_user(user: UserCreate,
                db:Annotated[Session ,Depends(get_db)]):
    is_user_exist = db.query(User).filter(User.email == user.email).first()

    if is_user_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User exists")
    
    # if not is_user_exist.is_verified:
    #     raise 

    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump()
    user_data.pop("password")    
    new_user = User(**user_data, hashed_password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "success": True,
        "Message": "User created Successfully"
    }

@router.post("/login", response_model=UserResponse)
def login(form_data: Annotated[OAuth2PasswordRequestForm , Depends()], 
          db: Annotated[Session, Depends(get_db)]):

    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not exists")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect password")

    tokens = create_tokens(data={"sub": str(user.id)})
    return {"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]}


@router.get("/refresh", response_model= UserResponse)
def get_access_token(db: Annotated[Session, Depends(get_db)],
                     current_user = Depends(get_current_user)):

    isUserExist = db.query(User).filter(User.id == current_user['sub']).first()

    if not isUserExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    

    tokens = create_tokens(data={"sub": str(isUserExist.id)})
    return {"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]}


@router.post("/change-password")
def change_password(
    data: ChangePassword,
    db: Annotated[Session, Depends(get_db)],
    current_user = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user['sub']).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(hashed_password=user.hashed_password,plain_password= data.current_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Password")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "Password Changed Successfully"}

