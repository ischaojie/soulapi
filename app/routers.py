from datetime import timedelta, datetime
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from lunar_python import Lunar
from pydantic import EmailStr
from redis import Redis
from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.config import settings
from app.depends import (
    get_db,
    get_current_active_superuser,
    get_current_confirm_user,
    get_current_user,
    get_redis_db,
    get_current_active_user,
)
from app.utils import (
    create_access_token,
    send_confirm_email,
    verify_confirm_token,
    send_test_email,
    send_reset_password_email,
)

psychologies_router = APIRouter()


@psychologies_router.get("/", response_model=List[schemas.Psychology])
def read_psychologies(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """read limited psychologies knowledge"""
    psychologies = crud.psychology.get_multi(db, skip=skip, limit=limit)
    return psychologies


@psychologies_router.post("/", response_model=schemas.Psychology)
def create_psychology(
        *,
        db: Session = Depends(get_db),
        psychology: schemas.PsychologyCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """create psychology knowledge, but only superuser can create."""
    return crud.psychology.create(db, obj=psychology)


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
        redis: Redis = Depends(get_redis_db),
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """read psychology random every day"""

    # 先从 redis 中取
    # redis 不存在或者不是当天的，从 db 中取
    # 同时写入 redis 缓存
    db_psychology = crud.psychology.get_psychology_daily(db, redis)
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
        current_user: models.User = Depends(get_current_active_superuser),
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
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """delete an psychology knowledge"""
    psychology_in_db = crud.psychology.get(db, pid)
    if not psychology_in_db:
        raise HTTPException(status_code=404, detail="psychology not found")
    psychology = crud.psychology.remove(db, id=pid)
    return psychology


# word router
word_router = APIRouter()


@word_router.post("/", response_model=schemas.Word)
def create_word(
        *,
        db: Session = Depends(get_db),
        word: schemas.WordCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """create word, but only superuser can create."""

    word_db = crud.word.get_by_origin(db, origin=word.origin)
    if word_db:
        raise HTTPException(status_code=400, detail="Word already exists")
    return crud.word.create(db, obj=word)


@word_router.delete("/{wid}", response_model=schemas.Word)
def delete_word(
        *,
        db: Session = Depends(get_db),
        wid: int,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """delete an word"""
    word_in_db = crud.word.get(db, wid)
    if not word_in_db:
        raise HTTPException(status_code=404, detail="word not found")
    word = crud.word.remove(db, id=wid)
    return word


@word_router.get("/daily", response_model=schemas.Word)
def read_word_daily(
        db: Session = Depends(get_db),
        redis: Redis = Depends(get_redis_db),
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """read word random every day"""

    db_word = crud.word.get_word_daily(db, redis)
    if not db_word:
        raise HTTPException(status_code=404, detail="word not found")
    return db_word


@word_router.get("/{wid}", response_model=schemas.Word)
def read_word(
        *,
        db: Session = Depends(get_db),
        wid: int,
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """get word by id"""
    db_word = crud.psychology.get(db, wid)
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found")
    return db_word


# user me

me_router = APIRouter()


@me_router.get("/", response_model=schemas.User)
def read_user_me(
        *,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    """read current login user"""
    return current_user


@me_router.put("/", response_model=schemas.User)
def update_user_me():
    """update current login user info"""
    pass


@me_router.post("/reset-password", response_model=schemas.Msg)
def reset_password(
        *,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
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


@me_router.post("/confirm-password", response_model=schemas.Msg)
def new_password_confirm(
        *,
        db: Session = Depends(get_db),
        token: str = Body(...),
        password: str = Body(...),
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """confirm user reset password"""
    # todo: send reset password mail need change url redirect to web addr
    email = verify_confirm_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # whether is current user
    if user.email != current_user.email:
        raise HTTPException(status_code=400, detail="Invalid User")

    # update user's password field
    user = crud.user.update(db, db_obj=user, obj={"password": password})

    return {"msg": "Password reset successfully"}


# user router
user_router = APIRouter()


@user_router.post("/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(get_db),
        user: schemas.UserCreate,
        current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """create user, only for superuser"""
    user_db = crud.user.get_by_email(db, email=user.email)
    if user_db:
        raise HTTPException(status_code=400, detail="User already exists")

    user = crud.user.create(db, obj=user, is_confirm=True)
    return user


@user_router.put("/{uid}", response_model=schemas.User)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(get_current_active_superuser),
):
    """update user, only for superuser"""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


# superuser crud user
@user_router.get("/", response_model=List[schemas.User])
def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
        current_user: models.User = Depends(get_current_active_superuser),
):
    """read all users, only for superuser"""
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


# login router
login_router = APIRouter()


@login_router.post("/register", response_model=schemas.User)
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


@login_router.post("/login", response_model=schemas.Token)
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


@login_router.post("/confirm", response_model=schemas.Msg)
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


# utils router
utils_router = APIRouter()


@utils_router.post("/test-email", response_model=schemas.Msg, status_code=201)
def test_email(
        email_to: EmailStr,
        background_tasks: BackgroundTasks,
        current_user: models.User = Depends(get_current_active_superuser),
):
    """test emails server"""
    background_tasks.add_task(send_test_email, email_to=email_to)
    return {"msg": "Test email sent"}


@utils_router.post("/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(get_current_user)) -> Any:
    """test token"""
    return current_user


@utils_router.get("/lunar", response_model=schemas.Lunar)
def lunar(
        current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """get current date in lunar"""

    lunar = Lunar.fromDate(datetime.now())
    return {
        "date": f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
        "ganzhi_year": lunar.getYearInGanZhi(),
        "ganzhi_month": lunar.getMonthInGanZhi(),
        "ganzhi_day": lunar.getDayInGanZhi(),
        "shengxiao": lunar.getYearShengXiao(),
    }
