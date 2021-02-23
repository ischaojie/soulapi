from datetime import timedelta, datetime
from pathlib import Path
from typing import Union, Any, Optional

import bcrypt
import emails
from jose import jwt, JWTError
from emails.template import JinjaTemplate as T
from loguru import logger

from app.config import settings


# security

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    generate jwt token
    :param subject: subject need to save in token
    :param expires_delta: expires time
    :return: token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.TOKEN_ALGORITHMS)
    return encoded_jwt


def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password, bcrypt.gensalt())


def verify_password(origin_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(origin_password, hashed_password)


# email

def send_email(email_to: str, subject_template: str = "", html_template: str = "", environment=None, ) -> None:
    """
    send email to some mail address
    :param email_to: send to this email
    :param subject_template: email subject
    :param html_template: email content
    :param environment: template params
    :return: email send response
    """
    if environment is None:
        environment = {}

    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"

    # email message
    message = emails.Message(
        subject=T(subject_template),
        html=T(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)
    )

    # smtp server
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    # send
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    subject = f"{settings.PROJECT_NAME} - Test email"

    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template = f.read()
    send_email(
        email_to,
        subject,
        template,
        {"project_name": settings.PROJECT_NAME, "email": email_to}
    )


def send_confirm_email(email_to: str, token: str) -> None:
    """send email verify user"""
    subject = f"{settings.PROJECT_NAME} - Verification link"
    with open() as f:
        content = f.read()

    link = f"{settings.SERVER_HOST}/confirm?token={token}"

    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=content,
        environment={
            "project_name": settings.PROJECT_NAME,
            "email": email_to,
            "link": link
        }
    )


def verify_confirm_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["email"]
    except jwt.PyJWTError:
        return None
