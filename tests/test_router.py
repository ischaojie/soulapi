import random
from typing import Generator, Dict

from faker import Faker
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app import schemas, crud
from app.config import settings
from app.database import SessionLocal
from app.main import app
from app.schemas import PsychologyClassifyEnum


def test_read_psychology_multi(client: TestClient, faker: Faker):
    client.get(f"{settings.API_V1_STR}/")


def create_random_psychologies(db: Session, faker: Faker):
    psychology = {
        "knowledge": faker.text(),
        "classify": random.choice(list(PsychologyClassifyEnum)).value,
    }

    obj_in = schemas.PsychologyCreate(**psychology)
    return crud.psychology.create(db, obj=obj_in)


def test_read_psychology_by_id(
    client: TestClient, db: Session, faker, get_superuser_token
):

    psychology = create_random_psychologies(db, faker)

    headers = {"Authorization": f"Bearer {get_superuser_token}"}

    rsp = client.get(
        f"{settings.API_V1_STR}/psychologies/{psychology.id}", headers=headers
    )
    assert rsp.status_code == 200
    assert psychology.classify == rsp.json()["classify"]
    assert psychology.knowledge == rsp.json()["knowledge"]


def test_post_psychology(client: TestClient, faker, get_superuser_token):

    headers = {"Authorization": f"Bearer {get_superuser_token}"}
    psychology = {
        "knowledge": faker.text(),
        "classify": random.choice(list(PsychologyClassifyEnum)).value,
    }

    rsp = client.post(
        f"{settings.API_V1_STR}/psychologies/", json=psychology, headers=headers
    )

    assert rsp.status_code == 200
    assert psychology["classify"] == rsp.json()["classify"]
    assert psychology["knowledge"] == rsp.json()["knowledge"]


def create_default_superuser(db: Session):
    superuser = schemas.UserCreate(
        full_name=settings.SUPERUSER_NAME,
        email=settings.SUPERUSER_EMAIL,
        password=settings.SUPERUSER_PASSWORD,
    )

    user = crud.user.get_by_email(db, email=settings.SUPERUSER_EMAIL)

    if user:
        return user

    user_db = crud.user.create_superuser(db, obj=superuser)
    return user_db


# test authorization
def test_login(client: TestClient, db: Session):

    create_default_superuser(db)

    login_data = {
        "username": settings.SUPERUSER_EMAIL,
        "password": settings.SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_token_authorization(client: TestClient, get_superuser_token: Dict[str, str]):
    headers = {"Authorization": f"Bearer {get_superuser_token}"}
    rsp = client.post(f"{settings.API_V1_STR}/utils/test-token", headers=headers)
    result = rsp.json()
    assert rsp.status_code == 200
    assert "email" in result


def test_register(monkeypatch, client: TestClient):
    monkeypatch.setenv("SOUL_API_USERS_OPEN_REGISTRATION", "True")


def test_forbidden_register(client: TestClient, monkeypatch):

    monkeypatch.setenv("SOUL_API_USERS_OPEN_REGISTRATION", "False")

    register_data = {
        "full_name": "test",
        "email": "test@example.com",
        "password": "123456",
    }

    rsp = client.post(f"{settings.API_V1_STR}/register", json=register_data)
    assert rsp.status_code == 403


def test_email_send():
    pass
