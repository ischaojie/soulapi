import random
from typing import Dict

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import schemas, crud
from app.config import settings
from app.schemas import PsychologyClassifyEnum
from tests.utils import (
    create_default_superuser,
    create_random_user,
    create_random_psychologies,
)


# test authorization
class TestLogin:
    @pytest.fixture(autouse=True)
    def _init_test(self, client: TestClient, db: Session, fake, get_superuser_token):
        self.client = client
        self.db = db
        self.token = get_superuser_token
        self.fake = fake

    def test_login(self):
        create_default_superuser(self.db)

        login_data = {
            "username": settings.SUPERUSER_EMAIL,
            "password": settings.SUPERUSER_PASSWORD,
        }
        r = self.client.post(f"{settings.API_V1_STR}/login", data=login_data)
        tokens = r.json()
        assert r.status_code == 200
        assert "access_token" in tokens
        assert tokens["access_token"]

    def test_token_authorization(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        rsp = self.client.post(
            f"{settings.API_V1_STR}/utils/test-token", headers=headers
        )
        result = rsp.json()
        assert rsp.status_code == 200
        assert "email" in result

    def test_register(self):
        settings.USERS_OPEN_REGISTRATION = True

        faker_user = {
            "full_name": self.fake.name(),
            "email": self.fake.email(),
            "password": "123456",
        }

        rsp = self.client.post(f"{settings.API_V1_STR}/register", json=faker_user)
        result = rsp.json()
        assert rsp.status_code == 200
        assert faker_user["full_name"] == result["full_name"]
        assert faker_user["email"] == result["email"]

    def test_forbidden_register(self):

        settings.USERS_OPEN_REGISTRATION = False

        register_data = {
            "full_name": "test",
            "email": "test@example.com",
            "password": "123456",
        }

        rsp = self.client.post(f"{settings.API_V1_STR}/register", json=register_data)
        assert rsp.status_code == 403
        assert "forbidden" in rsp.json()["detail"]

    def test_register_user_exists(self):
        settings.USERS_OPEN_REGISTRATION = True

        random_user = create_random_user(self.db, self.fake)

        faker_user = {
            "full_name": random_user.full_name,
            "email": random_user.email,
            "password": "123456",
        }

        rsp = self.client.post(f"{settings.API_V1_STR}/register", json=faker_user)

        assert rsp.status_code == 400
        assert "exists" in rsp.json()["detail"]


class TestEmail:
    def test_email_send(self):
        pass

    def test_email_user_confirm(self):
        pass

    def test_email_reset_password(self):
        pass


class TestPsychology:
    @pytest.fixture(autouse=True)
    def _init_test(self, client: TestClient, db: Session, fake, get_superuser_token):
        self.client = client
        self.db = db
        self.get_superuser_token = get_superuser_token
        self.fake = fake

    def test_read_psychology_multi(self):

        rsp = self.client.get(f"{settings.API_V1_STR}/psychologies")

    def test_read_psychology_by_id(self):

        random_psy = create_random_psychologies(self.db, self.fake)

        token = self.get_superuser_token
        headers = {"Authorization": f"Bearer {token}"}

        rsp = self.client.get(
            f"{settings.API_V1_STR}/psychologies/{random_psy.id}", headers=headers
        )
        assert rsp.status_code == 200
        assert random_psy.classify == rsp.json()["classify"]
        assert random_psy.knowledge == rsp.json()["knowledge"]

    def test_post_psychology(self):
        headers = {"Authorization": f"Bearer {self.get_superuser_token}"}
        psychology = {
            "knowledge": self.fake.text(),
            "classify": random.choice(list(PsychologyClassifyEnum)).value,
        }

        rsp = self.client.post(
            f"{settings.API_V1_STR}/psychologies/", json=psychology, headers=headers
        )

        assert rsp.status_code == 200
        assert psychology["classify"] == rsp.json()["classify"]
        assert psychology["knowledge"] == rsp.json()["knowledge"]

    def test_delete_psychology(self):
        random_psy = create_random_psychologies(self.db, self.fake)

        token = self.get_superuser_token
        headers = {"Authorization": f"Bearer {token}"}

        rsp = self.client.delete(
            f"{settings.API_V1_STR}/psychologies/{random_psy.id}", headers=headers
        )

        assert rsp.status_code == 200
