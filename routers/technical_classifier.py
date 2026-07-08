from graph.state import SupportState, TechnicalIssue


TECHNICAL_KEYWORDS: dict[TechnicalIssue, tuple[str, ...]] = {
    "application_error": (
        "error",
        "crash",
        "crashing",
        "blank screen",
        "exception",
    ),
    "performance_issue": (
        "slow",
        "lag",
        "lagging",
        "freezing",
        "takes too long",
    ),
    "feature_issue": (
        "button doesn't work",
        "button does not work",
        "button not responding",
        "button not working",
        "feature not working",
        "unable to upload",
        "cannot upload",
    ),
    "other_technical": (),
}


def classify_technical_issue(state: SupportState) -> dict:
    message = state["processed_message"].lower()

    for technical_issue, keywords in TECHNICAL_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            return {
                "technical_issue": technical_issue
            }

    return {
        "technical_issue": "other_technical"
    }