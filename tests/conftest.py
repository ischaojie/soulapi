from typing import Generator

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app import schemas, crud
from app.config import settings
from app.database import SessionLocal, init_db
from app.main import app
from faker import Faker


@pytest.fixture(scope="session")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def db(monkeysession) -> Generator:
    # set sqlite in memory
    monkeysession.setenv("SOUL_API_DATABASE_URI", "sqlite://")
    # init all tables
    init_db()
    session = SessionLocal()
    yield session


@pytest.fixture(scope="module", autouse=True)
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def get_superuser_token(client: TestClient):
    login_data = {
        "username": settings.SUPERUSER_EMAIL,
        "password": settings.SUPERUSER_PASSWORD,
    }
    rsp = client.post(f"{settings.API_V1_STR}/login", data=login_data)
    return rsp.json()["access_token"]


@pytest.fixture(scope="session")
def faker():
    yield Faker()
