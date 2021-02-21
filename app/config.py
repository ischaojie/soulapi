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
    ACCESS_TOKEN_EXPIRE: int = 60 * 24 * 7
    EMAIL_CONFIRM_TOKEN_EXPIRE: int = 60 * 2  # expire after 2 hour
    # email
    SMTP_TLS: bool = True  # smtp use TLS
    SMTP_PORT: Optional[int] = None  # smtp port
    SMTP_HOST: Optional[str] = None  # smtp host
    SMTP_USER: Optional[str] = None  # smtp user
    SMTP_PASSWORD: Optional[str] = None  # smtp password

    EMAILS_ENABLED: bool = True  # if email enabled

    @validator("EMAILS_ENABLED")
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(values.get("SMTP_HOST") and values.get("SMTP_PORT") and values.get("EMAILS_FROM_EMAIL"))

    EMAILS_FROM_NAME: Optional[str] = None  # email from name (soul)
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None  # email from (admin@soul.fun)

    EMAIL_TEMPLATES_DIR: str = "/app/email-templates"  # email templates dir

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # test email count

    class Config:
        case_sensitive = True


settings = Settings()
