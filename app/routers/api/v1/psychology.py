from typing import List, Any

from fastapi import Depends, HTTPException
from redis import Redis
from sqlalchemy.orm import Session

from app.crud.psychology import psychology
from app.depends import get_db, get_current_confirm_user, get_current_active_superuser, get_redis_db
from app.models.user import User
from app.schemas.psychology import Psychology, PsychologyUpdate, PsychologyCreate
from . import v1


@v1.get("/", response_model=List[Psychology])
def read_psychologies(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
        current_user: User = Depends(get_current_confirm_user),
) -> Any:
    """read limited psychologies knowledge"""
    psychologies = psychology.get_multi(db, skip=skip, limit=limit)
    return psychologies


@v1.post("/", response_model=Psychology)
def create_psychology(
        *,
        db: Session = Depends(get_db),
        psychology: PsychologyCreate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """create psychology knowledge, but only superuser can create."""
    return psychology.create(db, obj=psychology)


@v1.get("/random", response_model=Psychology)
def read_psychology_random(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_confirm_user),
) -> Any:
    """read psychology random"""
    db_psychology = psychology.get_psychology_random(db)
    if not db_psychology:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology


@v1.get("/daily", response_model=Psychology)
def read_psychology_daily(
        db: Session = Depends(get_db),
        redis: Redis = Depends(get_redis_db),
        current_user: User = Depends(get_current_confirm_user),
) -> Any:
    """read psychology random every day"""

    # 先从 redis 中取
    # redis 不存在或者不是当天的，从 db 中取
    # 同时写入 redis 缓存
    db_psychology = psychology.get_psychology_daily(db, redis)
    if not db_psychology:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology


@v1.get("/{pid}", response_model=Psychology)
def read_psychology(
        *,
        db: Session = Depends(get_db),
        pid: int,
        current_user: User = Depends(get_current_confirm_user),
) -> Any:
    """read psychology by id"""
    db_psychology = psychology.get(db, pid)
    if not db_psychology:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology


@v1.put("/{pid}", response_model=Psychology)
def update_psychology(
        *,
        db: Session = Depends(get_db),
        pid: int,
        psychology: PsychologyUpdate,
        current_user: User = Depends(get_current_active_superuser),
):
    """update psychology, only superuser"""
    psychology_in_db = psychology.get(db, pid)
    if not psychology_in_db:
        raise HTTPException(status_code=404, detail="psychology not found")

    psychology = psychology.update(db, db_obj=psychology_in_db, obj=psychology)
    return psychology


@v1.delete("/{pid}", response_model=Psychology)
def delete_psychology(
        *,
        db: Session = Depends(get_db),
        pid: int,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """delete an psychology knowledge"""
    psychology_in_db = psychology.get(db, pid)
    if not psychology_in_db:
        raise HTTPException(status_code=404, detail="psychology not found")
    psycholog = psychology.remove(db, id=pid)
    return psycholog
