from graph.state import SupportState


def billing_support(state: SupportState) -> dict:
    return {
        "response": (
            f"Your billing request has been received: "
            f"{state['processed_message']}"
        )
    }


def technical_support(state: SupportState) -> dict:
    return {
        "response": (
            f"Your technical support request has been received: "
            f"{state['processed_message']}"
        )
    }


def account_support(state: SupportState) -> dict:
    return {
        "response": (
            f"Your account support request has been received: "
            f"{state['processed_message']}"
        )
    }


def general_support(state: SupportState) -> dict:
    return {
        "response": (
            f"Your general question has been received: "
            f"{state['processed_message']}"
        )
    }


def fallback_support(state: SupportState) -> dict:
    return {
        "response": (
            "Sorry, I could not determine the type of support you need. "
            "Please provide more details about your request."
        ),
        "escalation_required": False,
    }