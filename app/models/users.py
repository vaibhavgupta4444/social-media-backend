from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    otp = Column(String(6), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_used = Column(Boolean, default=False)

    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete"
    )

    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())