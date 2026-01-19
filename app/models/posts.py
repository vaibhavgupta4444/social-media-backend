from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    content = Column(Text, nullable=True)
    media_url = Column(String, nullable=True)

    is_private = Column(Boolean, default=False)
    likes_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan"
    )
    likes = relationship(
        "Like",
        back_populates="post",
        cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")