import secrets
from typing import Optional, Any, Dict

from pydantic import BaseSettings, PostgresDsn, EmailStr, validator


class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY = secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    # token 过期时间
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # email server
    SMTP_TLS: bool = True  # smtp use TLS
    SMTP_PORT: Optional[int] = None  # smtp port
    SMTP_HOST: Optional[str] = None  # smtp host
    SMTP_USER: Optional[str] = None  # smtp user
    SMTP_PASSWORD: Optional[str] = None  # smtp password

    EMAILS_ENABLED: bool = True
    EMAILS_FROM_NAME: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    class Config:
        case_sensitive = True


settings = Settings()
