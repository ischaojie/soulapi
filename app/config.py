import secrets
from typing import Optional, Any, Dict, Union

from pydantic import BaseSettings, PostgresDsn, EmailStr, validator


class Settings(BaseSettings):
    """default config value"""

    PROJECT_NAME: str = "Soul"  # project name
    API_V1_STR: str = "/v1"  # api endpoint
    SERVER_HOST: str = "http://127.0.0.1:8000"
    SECRET_KEY: str = "I love lan"  # secret key for token
    TOKEN_ALGORITHMS: str = "HS256"  # algorithms
    USERS_OPEN_REGISTRATION: bool = True  # whether open user register
    DATABASE_URI: Union[str, PostgresDsn] = "sqlite:///./app.db"  # database url

    # redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: str = "0"

    # token expire time
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE: int = 60 * 24 * 7
    EMAIL_CONFIRM_TOKEN_EXPIRE: int = 60 * 2  # email confirm token expired after 2 hour

    # email
    # smtp default use aliyun
    SMTP_SSL: bool = True  # smtp use SSL
    SMTP_PORT: Optional[int] = 465  # smtp port
    SMTP_HOST: Optional[str] = "smtp.163.com"  # smtp host
    SMTP_USER: Optional[str] = "soulapi"  # smtp user
    SMTP_PASSWORD: Optional[str] = "KFMBEGZYNIBLBRYQ"  # smtp password

    EMAILS_FROM_NAME: Optional[str] = "soulapi"  # email from name
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "soulapi@163.com"  # email from

    EMAIL_TEMPLATES_DIR: str = "email-templates"  # email templates dir

    EMAILS_ENABLED: bool = True  # if email enabled

    @validator("EMAILS_ENABLED")
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # test email count

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
