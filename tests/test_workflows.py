from workflows.account.builder import build_account_graph
from workflows.billing.builder import build_billing_graph
from workflows.general.builder import build_general_graph
from workflows.technical.builder import build_technical_graph


def test_billing_workflow_duplicate_charge():
    graph = build_billing_graph()

    result = graph.invoke(
        {
            "processed_message": "I was charged twice",
        }
    )

    assert result["billing_issue"] == "duplicate_charge"
    assert "response" in result


def test_technical_workflow_resolved():
    graph = build_technical_graph()

    result = graph.invoke(
        {
            "processed_message": "The application keeps crashing",
        }
    )

    assert result["technical_issue"] == "application_error"
    assert result["resolution_status"] == "resolved"
    assert "response" in result


def test_technical_workflow_escalation():
    graph = build_technical_graph()

    result = graph.invoke(
        {
            "processed_message": "I have a strange technical problem",
        }
    )

    assert result["technical_issue"] == "other_technical"
    assert result["resolution_status"] == "unresolved"
    assert result["escalation_required"] is True
    assert result["escalation_reason"] == "automatic_diagnosis_failed"


def test_account_workflow_login():
    graph = build_account_graph()

    result = graph.invoke(
        {
            "processed_message": "I cannot log into my account",
        }
    )

    assert result["account_issue"] == "login_problem"
    assert "response" in result


def test_account_workflow_sensitive_request():
    graph = build_account_graph()

    result = graph.invoke(
        {
            "processed_message": "Delete my account",
        }
    )

    assert result["account_issue"] == "account_deletion"
    assert result["escalation_required"] is True
    assert result["escalation_reason"] == "sensitive_request"


def test_general_workflow_pricing():
    graph = build_general_graph()

    result = graph.invoke(
        {
            "processed_message": "Tell me about your pricing",
        }
    )

    assert result["general_issue"] == "pricing_question"
    assert "response" in result