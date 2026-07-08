from graph.state import SupportState


GENERAL_KEYWORDS = {
    "pricing_question": (
        "pricing",
        "price",
        "cost",
        "plans",
        "subscription plans",
    ),
    "product_question": (
        "features",
        "documentation",
        "how does it work",
        "what does the product do",
        "product information",
    ),
    "other_general": (),
}


def classify_general_issue(state: SupportState) -> dict:
    message = state["processed_message"].lower()

    for general_issue, keywords in GENERAL_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            return {
                "general_issue": general_issue
            }

    return {
        "general_issue": "other_general"
    }