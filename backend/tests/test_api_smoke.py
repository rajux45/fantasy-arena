from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="module")
def client():
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    from sqlalchemy.pool import StaticPool

    from app.db import Base
    from app.deps import get_db
    from app.main import app

    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(test_engine, expire_on_commit=False, future=True)

    def override():
        s = TestSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)


def test_root_health(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200


def test_signup_login_flow(client):
    email = f"u-{uuid.uuid4().hex[:6]}@example.com"
    r = client.post("/v1/auth/signup/email", json={"email": email, "password": "PassWord-123"})
    assert r.status_code == 201, r.text
    tokens = r.json()
    assert tokens["access_token"]

    r2 = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r2.status_code == 200
    assert r2.json()["email"] == email


def test_unauthenticated_me_rejected(client):
    r = client.get("/v1/auth/me")
    assert r.status_code == 401


def test_login_email(client):
    email = f"u-{uuid.uuid4().hex[:6]}@example.com"
    client.post("/v1/auth/signup/email", json={"email": email, "password": "PassWord-123"})
    r = client.post("/v1/auth/login/email", json={"email": email, "password": "PassWord-123"})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_login_wrong_password(client):
    email = f"u-{uuid.uuid4().hex[:6]}@example.com"
    client.post("/v1/auth/signup/email", json={"email": email, "password": "PassWord-123"})
    r = client.post("/v1/auth/login/email", json={"email": email, "password": "wrong-pass"})
    assert r.status_code == 401
