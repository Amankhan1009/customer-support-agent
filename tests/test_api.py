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
async def api_test_lifespan(app):
    # Override settings for test isolation
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


app.router.lifespan_context = api_test_lifespan


# ── Auth helper ───────────────────────────────────────────────────────────────

def get_test_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        json={
            "username": TEST_ADMIN_USERNAME,
            "password": TEST_ADMIN_PASSWORD,
        },
    )
    return response.json()["access_token"]


def auth_headers(client: TestClient) -> dict:
    return {"Authorization": f"Bearer {get_test_token(client)}"}


# ── Existing tests (updated with auth headers) ────────────────────────────────

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
            headers=auth_headers(client),
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
            headers=auth_headers(client),
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
        headers = auth_headers(client)

        first_response = client.post(
            "/support",
            json={
                "thread_id": "test-resume-1",
                "message": "I have a strange technical problem.",
            },
            headers=headers,
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
            headers=headers,
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
        headers = auth_headers(client)

        client.post(
            "/support",
            json={
                "thread_id": "test-status-1",
                "message": "I was charged twice.",
            },
            headers=headers,
        )

        response = client.get(
            "/support/test-status-1",
            headers=headers,
        )

        data = response.json()

        assert response.status_code == 200
        assert data["thread_id"] == "test-status-1"
        assert data["status"] == "completed"


def test_resume_non_paused_thread_returns_conflict():
    with TestClient(app) as client:
        headers = auth_headers(client)

        client.post(
            "/support",
            json={
                "thread_id": "test-conflict-1",
                "message": "I was charged twice.",
            },
            headers=headers,
        )

        response = client.post(
            "/support/resume",
            json={
                "thread_id": "test-conflict-1",
                "human_response": "Reviewed.",
            },
            headers=headers,
        )

        assert response.status_code == 409


def test_unknown_thread_returns_not_found():
    with TestClient(app) as client:
        response = client.get(
            "/support/thread-that-does-not-exist",
            headers=auth_headers(client),
        )

        assert response.status_code == 404


# ── Bug 1 regression ──────────────────────────────────────────────────────────

def test_unauthorized_billing_triggers_hitl():
    with TestClient(app) as client:
        response = client.post(
            "/support",
            json={
                "thread_id": "test-billing-escalation-1",
                "message": (
                    "I see fraudulent unauthorized charges on my billing statement. "
                    "I need to speak with a human agent immediately."
                ),
            },
            headers=auth_headers(client),
        )

        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "human_review_required"
        assert data["interrupt_data"] is not None
        assert data["interrupt_data"]["intent"] == "billing"
        assert data["interrupt_data"]["escalation_reason"] == "sensitive_request"
        assert data["response"] is None


def test_billing_hitl_resume():
    with TestClient(app) as client:
        headers = auth_headers(client)

        first = client.post(
            "/support",
            json={
                "thread_id": "test-billing-resume-2",
                "message": (
                    "I see fraudulent unauthorized charges on my billing statement. "
                    "I need to speak with a human agent immediately."
                ),
            },
            headers=headers,
        )

        assert first.json()["status"] == "human_review_required"

        resume = client.post(
            "/support/resume",
            json={
                "thread_id": "test-billing-resume-2",
                "human_response": "A billing specialist will contact you within 24 hours.",
            },
            headers=headers,
        )

        data = resume.json()

        assert resume.status_code == 200
        assert data["status"] == "completed"
        assert data["response"] == "A billing specialist will contact you within 24 hours."
        assert data["interrupt_data"] is None


# ── Bug 2 regression ──────────────────────────────────────────────────────────

def test_context_switching_does_not_fallback():
    from unittest.mock import MagicMock, patch

    from langchain_core.runnables import RunnableLambda

    from schemas.routing import IntentClassification

    call_count = [0]
    llm_responses = [
        IntentClassification(intent="billing"),
        IntentClassification(intent="general"),
        IntentClassification(intent="billing"),
    ]

    def fake_classify(_):
        result = llm_responses[call_count[0]]
        call_count[0] += 1
        return result

    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = RunnableLambda(fake_classify)

    with patch("routers.llm_classifier.get_llm", return_value=mock_llm):
        with TestClient(app) as client:
            headers = auth_headers(client)

            r1 = client.post(
                "/support",
                json={
                    "thread_id": "test-context-retention-1",
                    "message": "Hi, I need an update on the status of my return for item #REF-99214.",
                },
                headers=headers,
            )
            assert r1.status_code == 200
            assert r1.json()["status"] == "completed"

            r2 = client.post(
                "/support",
                json={
                    "thread_id": "test-context-retention-1",
                    "message": "Wait, before that, what are your customer support operating hours on Sundays?",
                },
                headers=headers,
            )
            assert r2.status_code == 200
            assert r2.json()["status"] == "completed"

            r3 = client.post(
                "/support",
                json={
                    "thread_id": "test-context-retention-1",
                    "message": "Understood. Now back to the item I mentioned first, what was its status?",
                },
                headers=headers,
            )
            data = r3.json()

            assert r3.status_code == 200
            assert data["status"] == "completed"
            assert "could not determine" not in (data.get("response") or "").lower()
            assert data.get("response") is not None

# ── Thread history tests ──────────────────────────────────────────────────────

def test_get_thread_history_empty_thread():
    with TestClient(app) as client:
        response = client.get(
            "/support/thread-with-no-history/history",
            headers=auth_headers(client),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == "thread-with-no-history"
        assert data["messages"] == []
        assert data["waiting_for_human"] is False


def test_get_thread_history_with_messages():
    with TestClient(app) as client:
        headers = auth_headers(client)
        thread_id = "test-history-thread-1"

        client.post(
            "/support",
            json={
                "thread_id": thread_id,
                "message": "I was charged twice.",
            },
            headers=headers,
        )

        response = client.get(
            f"/support/{thread_id}/history",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == thread_id
        assert len(data["messages"]) >= 2
        assert data["messages"][0]["role"] == "user"
        assert "charged twice" in data["messages"][0]["content"]
        assert data["messages"][1]["role"] == "assistant"


def test_get_thread_history_without_auth_returns_401():
    with TestClient(app) as client:
        response = client.get("/support/any-thread/history")
        assert response.status_code == 401