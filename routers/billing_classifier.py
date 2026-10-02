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
        "return",
        "item return",
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

    # Check direct keywords
    for billing_issue, keywords in BILLING_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            return {
                "billing_issue": billing_issue
            }

    # Contextual check: if follow-up refers to return/order from previous messages or state
    messages = state.get("messages", [])
    has_prior_context = (
        bool(state.get("order_id") or state.get("return_id"))
        or any(
            any(k in getattr(m, "content", "").lower() for k in ("return", "order", "refund"))
            for m in messages
        )
    )
    if has_prior_context and any(w in message for w in ("item", "status", "number", "earlier", "that", "order")):
        return {
            "billing_issue": "refund_request"
        }

    return {
        "billing_issue": "other_billing"
    }