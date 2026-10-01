"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.bot import Yuuki
from src.config import Config
from src.data import DataStore
from src.model import User
from src.webadmin import WebAdmin


class FakeBot(Yuuki):
    """A Yuuki without a LINE connection."""

    name = "Yuuki"
    version = "v8.0"

    def __init__(self, tmp_root: Path) -> None:  # noqa: D107 - test stub
        self.config = Config()
        self.data = DataStore(
            data_path=str(tmp_root / "d"), log_path=str(tmp_root / "l")
        )
        self.profile = User(
            mid="u1", displayName="Yuuki", statusMessage="hi"
        )
        self.helpers = {}


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    admin = WebAdmin(FakeBot(tmp_path), password="secret")
    with TestClient(admin.app) as test_client:
        yield test_client


@pytest.fixture
def authorized_client(client: TestClient) -> TestClient:
    response = client.post("/api/verify", data={"code": "secret"})
    assert response.json()["status"] == 200
    client.cookies.update(response.cookies)
    return client


def test_index_serves_alpine_app(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "alpinejs" in response.text
    assert "vue" not in response.text.lower()


def test_static_assets(client: TestClient) -> None:
    assert client.get("/static/js/app.js").status_code == 200
    assert client.get("/static/css/main.css").status_code == 200


def test_logo_is_plain_data_uri(client: TestClient) -> None:
    response = client.get("/logo")
    assert response.status_code == 200
    assert response.text.startswith("data:image/png")


def test_api_requires_session(client: TestClient) -> None:
    assert client.get("/api/profile").json()["status"] == 403


def test_verify_rejects_wrong_password(client: TestClient) -> None:
    response = client.post("/api/verify", data={"code": "wrong"})
    assert response.json()["status"] == 401


def test_api_authorized_endpoints(authorized_client: TestClient) -> None:
    profile = authorized_client.get("/api/profile").json()
    assert profile == {
        "id": "u1",
        "version": "v8.0",
        "name": "Yuuki",
        "status": "hi",
        "picture": None,
    }
    assert authorized_client.get("/api/groups").json() == []
    assert authorized_client.get("/api/helpers").json() == []
    assert authorized_client.get("/api/events/JoinGroup").json() == []
    assert authorized_client.get("/api/events/Nope").json()["status"] == 404
    settings = authorized_client.get("/api/settings").json()
    assert settings["security_service"] is False
