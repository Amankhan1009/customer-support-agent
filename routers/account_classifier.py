from graph.state import AccountIssue, SupportState


ACCOUNT_KEYWORDS: dict[AccountIssue, tuple[str, ...]] = {
    "suspicious_access": (
        "hacked",
        "someone accessed my account",
        "someone logging into my account",
        "someone logged into my account",
        "without my permission",
        "without permission",
        "unauthorized access",
        "suspicious login",
        "unrecognized login",
        "account compromised",
    ),
    "account_deletion": (
        "delete my account",
        "close my account",
        "remove my account",
    ),
    "password_reset": (
        "forgot password",
        "forgot my password",
        "forgot my account password",
        "reset password",
        "reset my password",
        "reset my account password",
        "change password",
        "change my password",
        "reset it",
    ),
    "login_problem": (
        "cannot log in",
        "can't log in",
        "unable to log in",
        "cannot login",
        "sign in problem",
    ),
    "account_management": (
        "change email",
        "update email",
        "change username",
        "update profile",
        "account settings",
    ),
    "other_account": (),
}


def classify_account_issue(state: SupportState) -> dict:
    message = state["processed_message"].lower()

    for account_issue, keywords in ACCOUNT_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            return {
                "account_issue": account_issue
            }

    # Semantic pattern: password + action (forgot / reset / change)
    if "password" in message and any(act in message for act in ("forgot", "reset", "change")):
        return {
            "account_issue": "password_reset"
        }

    return {
        "account_issue": "other_account"
    }