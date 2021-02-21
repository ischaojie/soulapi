from datetime import timedelta
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.config import settings
from app.depends import get_db, get_current_active_superuser, get_current_confirm_user
from app.utils import create_access_token, send_confirm_email, verify_confirm_token

psychologies_router = APIRouter()


@psychologies_router.get("/", response_model=List[schemas.Psychology])
def read_psychologies(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """read limited psychologies knowledge"""
    psychologies = crud.psychology.get_multi(db, skip, limit)
    return psychologies


@psychologies_router.post("/", response_model=schemas.Psychology)
def create_psychology(
        *,
        db: Session = Depends(get_db),
        psychology: schemas.PsychologyCreate,
        current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """create psychology knowledge, but only superuser can create."""
    return crud.psychology.create(db, psychology)


@psychologies_router.get("/random", response_model=schemas.Psychology)
def read_psychology_random(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """read psychology random"""
    db_psychology = crud.psychology.get_psychology_random(db)
    if not db_psychology:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology


@psychologies_router.get("/daily", response_model=schemas.Psychology)
def read_psychology_daily(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """read psychology random every day"""
    # todo
    # 先从 redis 中取
    # redis 不存在或者不是当天的，从 db 中取
    # 同时写入 redis 缓存
    db_psychology = crud.psychology.get_psychology_daily(db)
    if not db_psychology:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology


@psychologies_router.get("/{pid}", response_model=schemas.Psychology)
def read_psychology(
        *,
        db: Session = Depends(get_db),
        pid: int,
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """read psychology by id"""
    db_psychology = crud.psychology.get(db, pid)
    if not db_psychology:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology


@psychologies_router.put("/{pid}", response_model=schemas.Psychology)
def update_psychology(
        *,
        db: Session = Depends(get_db),
        pid: int,
        psychology: schemas.PsychologyUpdate,
        current_user: models.User = Depends(get_current_active_superuser)
):
    """update psychology, only superuser"""
    psychology_in_db = crud.psychology.get(db, pid)
    if not psychology_in_db:
        raise HTTPException(status_code=404, detail="psychology not found")

    psychology = crud.psychology.update(db, db_obj=psychology_in_db, obj=psychology)
    return psychology


@psychologies_router.delete("/{pid}", response_model=schemas.Psychology)
def delete_psychology(
        *,
        db: Session = Depends(get_db),
        pid: int,
        current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """delete an psychology knowledge"""
    psychology_in_db = crud.psychology.get(db, pid)
    if not psychology_in_db:
        raise HTTPException(status_code=404, detail="psychology not found")
    psychology = crud.psychology.remove(db, pid)
    return psychology


# user router
user_router = APIRouter()


@user_router.post("/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(get_db),
        user: schemas.UserCreate,
        current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """create user, only superuser can create"""
    user = crud.user.get_by_email(db, user.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = crud.user.create(db, user)
    return user


# login router
login_router = APIRouter()


@login_router.post("/register", response_model=schemas.User)
def register(
        *,
        db: Session = Depends(get_db),
        password: str = Body(...),
        email: EmailStr = Body(...),
        full_name: str = Body(None),
):
    """
    register a new user
    :param db: db session
    :param password: password
    :param email: email (unique)
    :param full_name: full name, can be black
    :return: created model
    """
    # why not use UserCreate schema? if used, user can control self become a superuser

    # only USERS_OPEN_REGISTRATION is True can register
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(status_code=403, detail="forbidden for register")

    user = crud.user.get_by_email(db, email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db, user_in)
    # send confirm email
    if settings.EMAILS_ENABLED and user.email:
        confirm_token = create_access_token(email, timedelta(settings.EMAIL_CONFIRM_TOKEN_EXPIRE))
        send_confirm_email(
            email_to=user.email,
            token=confirm_token
        )
    return user


@login_router.post("/login", response_model=schemas.Token)
def login(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    """login to get access token"""
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    token = {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }
    return token


@login_router.post("/confirm", response_model=schemas.Msg)
def confirm(
        db: Session = Depends(get_db),
        token: str = Body(...),
):
    """confirm registered user"""
    email = verify_confirm_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = crud.user.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # update confirm
    user = crud.user.update(db, db_obj=user, obj={"is_confirm": True})
    if not user.is_confirm:
        raise HTTPException(status_code=400, detail="Confirmed error")
    return {"msg": "Confirm user successfully"}