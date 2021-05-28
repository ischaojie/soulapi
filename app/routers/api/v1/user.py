from datetime import timedelta
from typing import Any, List

from app.user import user
from fastapi import Depends, Body, HTTPException
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.config import settings
from app.depends import get_db, get_current_active_user, get_current_active_superuser
from app.models.user import User
from app.schemas.base import Msg
from app.schemas.user import UserCreate, UserUpdate
from app.utils import create_access_token, send_reset_password_email, verify_confirm_token
from . import v1


@v1.get("/me", response_model=User)
def read_user_me(
        *,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    """read current login user"""
    return current_user


@v1.put("/me", response_model=User)
def update_user_me():
    """update current login user info"""
    pass


@v1.post("/reset-password", response_model=Msg)
def reset_password(
        *,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
        background_tasks: BackgroundTasks,
):
    """reset current user password"""
    email = current_user.email

    # send confirm email
    if settings.EMAILS_ENABLED and email:
        confirm_token = create_access_token(
            subject=email, expires_delta=timedelta(settings.EMAIL_CONFIRM_TOKEN_EXPIRE)
        )
        background_tasks.add_task(
            send_reset_password_email, email_to=email, token=confirm_token
        )
    return {"msg": "Password reset email sent"}


@v1.post("/confirm-password", response_model=Msg)
def new_password_confirm(
        *,
        db: Session = Depends(get_db),
        token: str = Body(...),
        password: str = Body(...),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """confirm user reset password"""
    # todo: send reset password mail need change url redirect to web addr
    email = verify_confirm_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    nuser = user.get_by_email(db, email=email)
    if not nuser:
        raise HTTPException(status_code=404, detail="User not found")

    # whether is current user
    if nuser.email != current_user.email:
        raise HTTPException(status_code=400, detail="Invalid User")

    # update user's password field
    nuser = user.update(db, db_obj=user, obj={"password": password})

    return {"msg": "Password reset successfully"}


@v1.post("/users", response_model=User)
def create_user(
        *,
        db: Session = Depends(get_db),
        user_schema: UserCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """create user, only for superuser"""
    user_now = user.get_by_email(db, email=user_schema.email)
    if user_now:
        raise HTTPException(status_code=400, detail="User already exists")

    user_now = user.create(db, obj=user_schema, is_confirm=True)
    return user_now


@v1.put("/users/{uid}", response_model=User)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        user_in: UserUpdate,
        current_user: User = Depends(get_current_active_superuser),
):
    """update user, only for superuser"""
    user_now = user.get(db, id=user_id)
    if not user_now:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user_now = user.update(db, db_obj=user_now, obj_in=user_in)
    return user_now


# superuser crud user
@v1.get("/users", response_model=List[User])
def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
        current_user: User = Depends(get_current_active_superuser),
):
    """read all users, only for superuser"""
    users = user.get_multi(db, skip=skip, limit=limit)
    return users
