from graph.state import SupportIntent, SupportState


INTENT_KEYWORDS: dict[SupportIntent, tuple[str, ...]] = {
    "billing": (
        "payment",
        "charged",
        "charge",
        "refund",
        "invoice",
        "billing",
    ),
    "technical": (
        "error",
        "bug",
        "crash",
        "crashing",
        "not working",
        "technical",
    ),
    "account": (
        "login",
        "log in",
        "password",
        "account",
        "sign in",
    ),
    "general": (
        "pricing",
        "features",
        "information",
    ),
    "unknown": (),
}


def classify_intent(state: SupportState) -> dict:
    message = state["processed_message"].lower()

    matched_intents: list[SupportIntent] = []

    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            matched_intents.append(intent)

    if len(matched_intents) == 1:
        return {
            "intent": matched_intents[0],
            "routing_source": "deterministic",
            "needs_llm_routing": False,
        }

    return {
        "intent": "unknown",
        "routing_source": "unresolved",
        "needs_llm_routing": True,
    }