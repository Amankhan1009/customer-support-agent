from graph.state import BillingIssue, SupportState


BILLING_KEYWORDS: dict[BillingIssue, tuple[str, ...]] = {
    "duplicate_charge": (
        "charged twice",
        "charged two times",
        "duplicate charge",
        "double charged",
        "deducted twice",
        "deducted two times",
    ),
    "refund_request": (
        "refund",
        "money back",
        "return my money",
        "refund request",
    ),
    "payment_failure": (
        "payment failed",
        "payment was declined",
        "payment declined",
        "card declined",
        "card was declined",
        "transaction failed",
        "transaction was declined",
        "unable to pay",
    ),
    "other_billing": (),
}


def classify_billing_issue(state: SupportState) -> dict:
    message = state["processed_message"].lower()

    for billing_issue, keywords in BILLING_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            return {
                "billing_issue": billing_issue
            }

    return {
        "billing_issue": "other_billing"
    }