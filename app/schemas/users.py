from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    access_token: str
    refresh_token: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str