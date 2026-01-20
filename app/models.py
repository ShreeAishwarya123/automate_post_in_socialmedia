"""
Database models for the Social Media Automation API
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    credentials = relationship("SocialMediaCredential", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")

class SocialMediaCredential(Base):
    """Social media credentials for each user"""
    __tablename__ = "social_media_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)  # instagram, facebook, youtube, linkedin
    credential_type = Column(String, nullable=False)  # api_key, access_token, username_password, etc.

    # Credential data (encrypted)
    credential_data = Column(JSON, nullable=False)  # Encrypted JSON with tokens/keys

    # Platform-specific fields
    account_name = Column(String)  # Display name or username
    account_id = Column(String)  # Platform-specific ID (page_id, channel_id, etc.)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="credentials")

class Post(Base):
    """Post model"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Content
    title = Column(String)
    content = Column(Text, nullable=False)
    content_type = Column(String, nullable=False)  # text, image, video

    # Media files
    media_url = Column(String)  # URL to uploaded media
    media_type = Column(String)  # image, video
    media_filename = Column(String)  # Original filename

    # Gemini settings (optional)
    use_gemini = Column(Boolean, default=False)
    gemini_prompt = Column(Text)

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True))
    is_scheduled = Column(Boolean, default=False)

    # Status
    status = Column(String, default="draft")  # draft, scheduled, posted, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="posts")
    platforms = relationship("PostPlatform", back_populates="post", cascade="all, delete-orphan", primaryjoin="Post.id == PostPlatform.post_id")

class PostPlatform(Base):
    """Platforms where the post should be published"""
    __tablename__ = "post_platforms"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    platform = Column(String, nullable=False)  # instagram, facebook, youtube, linkedin
    status = Column(String, default="pending")  # pending, posted, failed

    # Platform-specific post data
    post_url = Column(String)  # URL to the posted content
    platform_post_id = Column(String)  # Platform's post ID
    error_message = Column(Text)

    posted_at = Column(DateTime(timezone=True))

    # Relationships
    post = relationship("Post", back_populates="platforms")