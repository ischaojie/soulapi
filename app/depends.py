# get db session
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    """get current user by token"""
    try:
        # verify jwt token
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=["HS256"])
        # unpack payload data
        token_data = schemas.TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    # get user by unpacked id
    user = db.query(models.User).get(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """current user is active ?"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(current_user: models.User = Depends(get_current_user)) -> models.User:
    """current active user is superuser"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user


def get_current_confirm_user(current_user: models.User = Depends(get_current_active_user)) -> models.User:
    if not current_user.is_confirm:
        raise HTTPException(status_code=400, detail="The user doesn't confirmed")
    return current_user
