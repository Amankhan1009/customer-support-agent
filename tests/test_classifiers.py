from routers.account_classifier import classify_account_issue
from routers.billing_classifier import classify_billing_issue
from routers.general_classifier import classify_general_issue
from routers.technical_classifier import classify_technical_issue


def test_billing_duplicate_charge():
    result = classify_billing_issue(
        {"processed_message": "I was charged twice"}
    )

    assert result["billing_issue"] == "duplicate_charge"


def test_billing_refund_request():
    result = classify_billing_issue(
        {"processed_message": "I want my money back"}
    )

    assert result["billing_issue"] == "refund_request"


def test_technical_application_error():
    result = classify_technical_issue(
        {"processed_message": "The application keeps crashing"}
    )

    assert result["technical_issue"] == "application_error"


def test_technical_feature_issue():
    result = classify_technical_issue(
        {"processed_message": "The upload button does not work"}
    )

    assert result["technical_issue"] == "feature_issue"


def test_account_login_problem():
    result = classify_account_issue(
        {"processed_message": "I cannot log into my account"}
    )

    assert result["account_issue"] == "login_problem"


def test_account_password_reset():
    result = classify_account_issue(
        {"processed_message": "I forgot my password"}
    )

    assert result["account_issue"] == "password_reset"


def test_general_pricing_question():
    result = classify_general_issue(
        {"processed_message": "Tell me about your pricing"}
    )

    assert result["general_issue"] == "pricing_question"