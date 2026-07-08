import os
import sqlite3
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from langgraph.checkpoint.sqlite import SqliteSaver

from api.main import app
from graph.builder import build_graph


TEST_DATABASE_PATH = "test_support_checkpoints.db"


@asynccontextmanager
async def api_test_lifespan(app):
    connection = sqlite3.connect(
        TEST_DATABASE_PATH,
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(connection)

    app.state.graph = build_graph(
        checkpointer=checkpointer,
    )

    app.state.connection = connection

    yield

    connection.close()

    if os.path.exists(TEST_DATABASE_PATH):
        os.remove(TEST_DATABASE_PATH)


app.router.lifespan_context = api_test_lifespan


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
        }


def test_support_completed_request():
    with TestClient(app) as client:
        response = client.post(
            "/support",
            json={
                "thread_id": "test-billing-1",
                "message": "I was charged twice.",
            },
        )

        data = response.json()

        assert response.status_code == 200
        assert data["thread_id"] == "test-billing-1"
        assert data["status"] == "completed"
        assert data["response"] is not None
        assert data["interrupt_data"] is None


def test_support_human_review_required():
    with TestClient(app) as client:
        response = client.post(
            "/support",
            json={
                "thread_id": "test-hitl-1",
                "message": "I have a strange technical problem.",
            },
        )

        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "human_review_required"
        assert data["response"] is None

        assert data["interrupt_data"]["intent"] == "technical"

        assert (
            data["interrupt_data"]["escalation_reason"]
            == "automatic_diagnosis_failed"
        )


def test_support_resume():
    with TestClient(app) as client:
        first_response = client.post(
            "/support",
            json={
                "thread_id": "test-resume-1",
                "message": "I have a strange technical problem.",
            },
        )

        assert first_response.status_code == 200
        assert (
            first_response.json()["status"]
            == "human_review_required"
        )

        resume_response = client.post(
            "/support/resume",
            json={
                "thread_id": "test-resume-1",
                "human_response": (
                    "A human engineer reviewed your request."
                ),
            },
        )

        data = resume_response.json()

        assert resume_response.status_code == 200
        assert data["status"] == "completed"
        assert (
            data["response"]
            == "A human engineer reviewed your request."
        )
        assert data["interrupt_data"] is None


def test_get_support_status():
    with TestClient(app) as client:
        client.post(
            "/support",
            json={
                "thread_id": "test-status-1",
                "message": "I was charged twice.",
            },
        )

        response = client.get(
            "/support/test-status-1"
        )

        data = response.json()

        assert response.status_code == 200
        assert data["thread_id"] == "test-status-1"
        assert data["status"] == "completed"


def test_resume_non_paused_thread_returns_conflict():
    with TestClient(app) as client:
        client.post(
            "/support",
            json={
                "thread_id": "test-conflict-1",
                "message": "I was charged twice.",
            },
        )

        response = client.post(
            "/support/resume",
            json={
                "thread_id": "test-conflict-1",
                "human_response": "Reviewed.",
            },
        )

        assert response.status_code == 409


def test_unknown_thread_returns_not_found():
    with TestClient(app) as client:
        response = client.get(
            "/support/thread-that-does-not-exist"
        )

        assert response.status_code == 404