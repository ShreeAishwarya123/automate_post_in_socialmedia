"""
Configuration settings for the Social Media Automation API
"""

import os
from pydantic_settings import BaseSettings
from pydantic import BaseModel

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./social_media_automation.db"

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application
    app_name: str = "Social Media Automation API"
    debug: bool = True

    # File upload
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "uploads"

    # Gemini settings (can be overridden per user)
    gemini_credentials_path: str = "gemini_automation/gemini_automation/auth/credentials.json"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()