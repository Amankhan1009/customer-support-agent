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

# ==================================================
# Bug 1 Regression — handle_other_billing escalation
# ==================================================

def test_billing_other_escalates_unauthorized_charges():
    from nodes.billing_nodes import handle_other_billing

    result = handle_other_billing({
        "processed_message": (
            "I see unauthorized charges of $450. "
            "I need to speak with a human agent immediately."
        )
    })

    assert result["escalation_required"] is True
    assert result["escalation_reason"] == "sensitive_request"
    assert "response" not in result


def test_billing_other_escalates_on_fraud():
    from nodes.billing_nodes import handle_other_billing

    result = handle_other_billing({
        "processed_message": "There is a fraudulent charge on my billing statement."
    })

    assert result["escalation_required"] is True
    assert result["escalation_reason"] == "sensitive_request"


def test_billing_other_escalates_on_account_compromise():
    from nodes.billing_nodes import handle_other_billing

    result = handle_other_billing({
        "processed_message": "My account was compromised and I need a human agent."
    })

    assert result["escalation_required"] is True
    assert result["escalation_reason"] == "sensitive_request"


def test_billing_other_preserves_normal_response():
    from nodes.billing_nodes import handle_other_billing

    result = handle_other_billing({
        "processed_message": "I have a question about my last invoice date."
    })

    assert "response" in result
    assert "additional review" in result["response"]
    assert "escalation_required" not in result


# ==================================================
# Bug 2 Regression — LLM classifier prompt and context
# ==================================================

def test_llm_prompt_removed_conflicting_instruction():
    from routers.llm_classifier import CLASSIFICATION_PROMPT

    system_template = CLASSIFICATION_PROMPT.messages[0].prompt.template

    assert (
        "Prioritize the latest customer message over older conversation history"
        not in system_template
    )


def test_llm_prompt_contains_referential_guidance():
    from routers.llm_classifier import CLASSIFICATION_PROMPT

    system_template = CLASSIFICATION_PROMPT.messages[0].prompt.template

    assert "referential" in system_template.lower()


def test_llm_build_context_includes_previous_messages():
    from langchain_core.messages import AIMessage, HumanMessage

    from routers.llm_classifier import build_conversation_context

    state = {
        "messages": [
            HumanMessage(content="I need help with item #REF-99214."),
            AIMessage(content="Your billing request is under review."),
            HumanMessage(content="What are your operating hours?"),  # latest — excluded
        ]
    }

    context = build_conversation_context(state)

    assert "#REF-99214" in context
    assert "billing request is under review" in context
    assert "operating hours" not in context


def test_llm_build_context_empty_when_no_previous_messages():
    from langchain_core.messages import HumanMessage

    from routers.llm_classifier import build_conversation_context

    state = {
        "messages": [
            HumanMessage(content="This is the only message."),
        ]
    }

    context = build_conversation_context(state)

    assert context == "No previous conversation context."

# ==================================================
# Fix Regression Tests (Issues A, B, C, D)
# ==================================================

def test_account_password_reset_natural_phrasing():
    result = classify_account_issue({
        "processed_message": "I forgot my account password and need to reset it."
    })
    assert result["account_issue"] == "password_reset"


def test_account_suspicious_login_natural_phrasing():
    result = classify_account_issue({
        "processed_message": "I received an email about someone logging into my account from another country without my permission."
    })
    assert result["account_issue"] == "suspicious_access"


def test_billing_return_status_classification():
    result = classify_billing_issue({
        "processed_message": "Hi, I need an update on the status of my return for item #REF-99214."
    })
    assert result["billing_issue"] == "refund_request"


def test_llm_prompt_instructs_original_topic_return():
    from routers.llm_classifier import CLASSIFICATION_PROMPT
    template = CLASSIFICATION_PROMPT.messages[0].prompt.template
    assert "the return I mentioned earlier" in template