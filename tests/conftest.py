from typing import Generator

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.database import init_db, SessionLocal
from app.main import app
from tests.utils import create_default_superuser


@pytest.fixture(scope="session")
def db() -> Generator:
    # init all tables
    init_db()
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def get_superuser_token(client: TestClient, db: Session):
    create_default_superuser(db)

    login_data = {
        "username": settings.SUPERUSER_EMAIL,
        "password": settings.SUPERUSER_PASSWORD,
    }
    rsp = client.post(f"{settings.API_V1_STR}/login", data=login_data)
    return rsp.json()["access_token"]


@pytest.fixture(scope="session")
def fake() -> Faker:
    fake = Faker()
    return fake
