from graph.state import SupportState


def handle_pricing_question(state: SupportState) -> dict:
    return {
        "response": (
            "We identified a pricing-related question. "
            "Please review the available plans and pricing information."
        )
    }


def handle_product_question(state: SupportState) -> dict:
    return {
        "response": (
            "We identified a general product question. "
            "Please review the product documentation for more information."
        )
    }


def handle_other_general(state: SupportState) -> dict:
    return {
        "response": (
            "We received your general support question. "
            "Please provide more details if you need additional assistance."
        )
    }