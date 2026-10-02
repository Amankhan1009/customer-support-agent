import os
import sqlite3
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from langgraph.checkpoint.sqlite import SqliteSaver

import config.settings as settings
from api.main import app
from auth.security import init_user_db
from graph.builder import build_graph


TEST_DATABASE_PATH = "test_support_checkpoints.db"
TEST_ADMIN_USERNAME = "testadmin"
TEST_ADMIN_PASSWORD = "testpassword"


@asynccontextmanager
async def auth_test_lifespan(app):
    settings.DATABASE_PATH = TEST_DATABASE_PATH
    settings.DEFAULT_ADMIN_USERNAME = TEST_ADMIN_USERNAME
    settings.DEFAULT_ADMIN_PASSWORD = TEST_ADMIN_PASSWORD

    connection = sqlite3.connect(
        TEST_DATABASE_PATH,
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(connection)

    app.state.graph = build_graph(
        checkpointer=checkpointer,
    )

    app.state.connection = connection

    init_user_db()

    yield

    connection.close()

    if os.path.exists(TEST_DATABASE_PATH):
        os.remove(TEST_DATABASE_PATH)


app.router.lifespan_context = auth_test_lifespan


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_valid_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        json={
            "username": TEST_ADMIN_USERNAME,
            "password": TEST_ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# ── Auth tests ────────────────────────────────────────────────────────────────

def test_login_success():
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={
                "username": TEST_ADMIN_USERNAME,
                "password": TEST_ADMIN_PASSWORD,
            },
        )

        data = response.json()

        assert response.status_code == 200
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0


def test_login_wrong_password():
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={
                "username": TEST_ADMIN_USERNAME,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]


def test_login_wrong_username():
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": TEST_ADMIN_PASSWORD,
            },
        )

        assert response.status_code == 401


def test_get_me_with_valid_token():
    with TestClient(app) as client:
        token = get_valid_token(client)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()

        assert response.status_code == 200
        assert data["username"] == TEST_ADMIN_USERNAME


def test_get_me_without_token():
    with TestClient(app) as client:
        response = client.get("/auth/me")

        assert response.status_code == 401


def test_get_me_with_invalid_token():
    with TestClient(app) as client:
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer this-is-not-a-valid-token"},
        )

        assert response.status_code == 401


def test_protected_support_without_token():
    with TestClient(app) as client:
        response = client.post(
            "/support",
            json={
                "thread_id": "test-no-auth",
                "message": "I need help.",
            },
        )

        assert response.status_code == 401


def test_protected_support_with_invalid_token():
    with TestClient(app) as client:
        response = client.post(
            "/support",
            json={
                "thread_id": "test-bad-token",
                "message": "I need help.",
            },
            headers={"Authorization": "Bearer bad.token.here"},
        )

        assert response.status_code == 401


def test_protected_support_with_valid_token():
    with TestClient(app) as client:
        token = get_valid_token(client)

        response = client.post(
            "/support",
            json={
                "thread_id": "test-auth-support-1",
                "message": "I was charged twice.",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "completed"


def test_health_still_public():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_get_status_without_token():
    with TestClient(app) as client:
        response = client.get("/support/some-thread")

        assert response.status_code == 401


def test_resume_without_token():
    with TestClient(app) as client:
        response = client.post(
            "/support/resume",
            json={
                "thread_id": "some-thread",
                "human_response": "Reviewed.",
            },
        )

        assert response.status_code == 401

def test_register_success():
    import uuid

    with TestClient(app) as client:
        unique_user = f"user_{uuid.uuid4().hex[:8]}"
        response = client.post(
            "/auth/register",
            json={
                "username": unique_user,
                "password": "secretpassword123",
            },
        )
        data = response.json()
        assert response.status_code == 201
        assert "access_token" in data

        # Verify new user can immediately call protected endpoints
        token = data["access_token"]
        me_resp = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == unique_user

def test_register_duplicate_username_fails():
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={
                "username": TEST_ADMIN_USERNAME,
                "password": "somepassword",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()