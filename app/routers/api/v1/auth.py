from datetime import timedelta

from fastapi import Depends, Body, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.sql import crud
from starlette import schemas
from starlette.background import BackgroundTasks

from app.config import settings
from app.depends import get_db
from app.utils import create_access_token, send_confirm_email, verify_confirm_token
from . import v1


@v1.post("/register", response_model=schemas.User)
def register(
        *,
        db: Session = Depends(get_db),
        password: str = Body(...),
        email: EmailStr = Body(...),
        full_name: str = Body(None),
        background_tasks: BackgroundTasks,
):
    """register a new user"""

    # why not use UserCreate schema? if used, user can control self become a superuser

    # only USERS_OPEN_REGISTRATION is True can register
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(status_code=403, detail="forbidden for register")

    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db, obj=user_in)

    # send confirm email
    if settings.EMAILS_ENABLED and user.email:
        confirm_token = create_access_token(
            subject=email, expires_delta=timedelta(settings.EMAIL_CONFIRM_TOKEN_EXPIRE)
        )
        background_tasks.add_task(
            send_confirm_email, email_to=user.email, token=confirm_token
        )

    return user


@v1.post("/login", response_model=schemas.Token)
def login(
        db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """login to get access token"""
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    token = {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }

    if user.is_superuser:
        token["access_token"] = create_access_token(user.id, is_superuser=True)
    return token


@v1.post("/confirm", response_model=schemas.Msg)
def confirm(
        *,
        db: Session = Depends(get_db),
        token: str = Body(...),
):
    """confirm registered user"""
    email = verify_confirm_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # update user's is_confirm field
    user = crud.user.update(db, db_obj=user, obj={"is_confirm": True})
    if not user.is_confirm:
        raise HTTPException(status_code=400, detail="Confirmed error")

    return {"msg": "Confirm user successfully"}
