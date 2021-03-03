import random

from faker import Faker
from sqlalchemy.orm import Session

from app import schemas, crud
from app.config import settings
from app.schemas import PsychologyClassifyEnum


def create_default_superuser(db: Session):
    superuser = schemas.UserCreate(
        full_name=settings.SUPERUSER_NAME,
        email=settings.SUPERUSER_EMAIL,
        password=settings.SUPERUSER_PASSWORD,
    )

    user = crud.user.get_by_email(db, email=settings.SUPERUSER_EMAIL)

    if user:
        return

    user_db = crud.user.create_superuser(db, obj=superuser)
    return user_db


def create_random_user(db: Session, fake: Faker):
    user = schemas.UserCreate(
        full_name=fake.name(), email=fake.email(), password="123456"
    )

    user_in_db = crud.user.get_by_email(db, email=user.email)
    if user_in_db:
        return user
    user_db = crud.user.create(db, obj=user)
    return user


def create_random_psychologies(db: Session, fake: Faker):
    psychology = {
        "knowledge": fake.text(),
        "classify": random.choice(list(PsychologyClassifyEnum)).value,
    }

    obj_in = schemas.PsychologyCreate(**psychology)
    return crud.psychology.create(db, obj=obj_in)
