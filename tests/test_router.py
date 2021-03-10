import os
import random
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from lunar_python import Lunar
from sqlalchemy.orm import Session

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
    @pytest.fixture(autouse=True)
    def _init_test(self, client: TestClient, db: Session, fake, get_superuser_token):
        self.client = client
        self.db = db
        self.token = get_superuser_token
        self.fake = fake

        SOUL_API_TEST_EMAIL_KEY = os.getenv("SOUL_API_TEST_EMAIL_KEY")
        SOUL_API_TEST_EMAIL_NAMESPACE = os.getenv("SOUL_API_TEST_EMAIL_NAMESPACE")

        self.test_email_url = (
            f"https://api.testmail.app/api/json?"
            f"apikey={SOUL_API_TEST_EMAIL_KEY}"
            f"&namespace={SOUL_API_TEST_EMAIL_NAMESPACE}"
            f"&&livequery=true"
        )

    def test_email_send(self):
        test_email_to = os.getenv("SOUL_API_TEST_EMAIL_USER")
        headers = {"Authorization": f"Bearer {self.token}"}
        send_rsp = self.client.post(
            f"{settings.API_V1_STR}/utils/test-email?email_to={test_email_to}",
            headers=headers,
        )
        print(send_rsp.json())
        assert send_rsp.status_code == 200
        assert "Test email sent" in send_rsp.json()["msg"]

        email_test_rsp = self.client.get(self.test_email_url, timeout=60)
        assert email_test_rsp.status_code == 200
        email_test = email_test_rsp.json()
        assert email_test["result"] == "success"
        assert email_test["count"] == 1
        assert "test email" in email_test["emails"][0]["html"]

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


class TestUtils:
    @pytest.fixture(autouse=True)
    def _init_test(self, client: TestClient, db: Session, fake, get_superuser_token):
        self.client = client
        self.db = db
        self.get_superuser_token = get_superuser_token
        self.fake = fake

    def test_lunar(self):
        lunar = Lunar.fromDate(datetime.now())
        token = self.get_superuser_token
        headers = {"Authorization": f"Bearer {token}"}
        rsp = self.client.get(f"{settings.API_V1_STR}/utils/lunar", headers=headers)
        assert rsp.status_code == 200
        result = rsp.json()

        assert (
            result["date"] == f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
        )
