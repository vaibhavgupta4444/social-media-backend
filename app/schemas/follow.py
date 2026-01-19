from pydantic import BaseModel
from typing import List


class FollowerResponse(BaseModel):
    username: str

    class Config:
        from_attributes = True


class FollowingResponse(BaseModel):
    username: str

    class Config:
        from_attributes = True


class FollowerListResponse(BaseModel):
    count: int
    followers: List[FollowerResponse]


class FollowingListResponse(BaseModel):
    count: int
    following: List[FollowingResponse]
