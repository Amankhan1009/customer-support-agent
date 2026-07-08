from graph.state import SupportState


def handle_login_problem(state: SupportState) -> dict:
    return {
        "response": (
            "We identified a login issue. Verify your credentials, "
            "check your network connection, and try signing in again."
        )
    }


def handle_password_reset(state: SupportState) -> dict:
    return {
        "response": (
            "We identified a password reset request. "
            "Use the password recovery process to securely reset your password."
        )
    }


def handle_account_management(state: SupportState) -> dict:
    return {
        "response": (
            "We identified an account management request. "
            "You can review and update supported account settings."
        )
    }


def handle_suspicious_access(state: SupportState) -> dict:
    return {
        "escalation_required": True,
        "escalation_reason": "sensitive_request",
    }


def handle_account_deletion(state: SupportState) -> dict:
    return {
        "escalation_required": True,
        "escalation_reason": "sensitive_request",
    }


def handle_other_account(state: SupportState) -> dict:
    return {
        "response": (
            "We could not automatically determine how to handle "
            "your account request. Please provide more details."
        )
    }