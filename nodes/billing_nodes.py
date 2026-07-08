from graph.state import SupportState


def handle_duplicate_charge(state: SupportState) -> dict:
    return {
        "response": (
            "We identified your request as a duplicate charge issue. "
            "The duplicate transaction will need to be reviewed."
        )
    }


def handle_refund_request(state: SupportState) -> dict:
    return {
        "response": (
            "We identified your request as a refund request. "
            "Your refund eligibility will need to be reviewed."
        )
    }


def handle_payment_failure(state: SupportState) -> dict:
    return {
        "response": (
            "We identified your request as a payment failure. "
            "Please verify your payment details or try another payment method."
        )
    }


def handle_other_billing(state: SupportState) -> dict:
    return {
        "response": (
            "Your billing request requires additional review. "
            "Please provide more details about the billing issue."
        )
    }