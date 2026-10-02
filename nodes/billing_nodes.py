import re

from graph.state import SupportState


def _resolve_entities(state: SupportState) -> tuple[str | None, str | None, str | None]:
    message = state.get("processed_message", "").lower()
    raw_message = state.get("processed_message", "")

    return_id = state.get("return_id")
    order_id = state.get("order_id")
    active_ref = state.get("reference_id")

    # 1. Explicit entity in the current message takes absolute precedence
    match = re.search(r"#?[A-Z]+-\d+", raw_message)
    if match:
        found = match.group(0)
        active_ref = found
        if "return" in message or found.startswith(("#REF", "REF")):
            return_id = found
        if "order" in message or found.startswith(("#ORD", "ORD")):
            order_id = found
    else:
        # 2. Referential query: recall specific entity type from state or conversation history
        if "return" in message:
            if return_id:
                active_ref = return_id
            else:
                for msg in reversed(state.get("messages", [])):
                    c = getattr(msg, "content", "") if not isinstance(msg, dict) else msg.get("content", "")
                    if "return" in c.lower() or "#ref" in c.lower() or "ref-" in c.lower():
                        m = re.search(r"#?[A-Z]+-\d+", c)
                        if m:
                            return_id = m.group(0)
                            active_ref = return_id
                            break
        elif "order" in message:
            if order_id:
                active_ref = order_id
            else:
                for msg in reversed(state.get("messages", [])):
                    c = getattr(msg, "content", "") if not isinstance(msg, dict) else msg.get("content", "")
                    if "order" in c.lower() or "#ord" in c.lower() or "ord-" in c.lower():
                        m = re.search(r"#?[A-Z]+-\d+", c)
                        if m:
                            order_id = m.group(0)
                            active_ref = order_id
                            break

    return active_ref, return_id, order_id


def handle_duplicate_charge(state: SupportState) -> dict:
    return {
        "response": (
            "We identified your request as a duplicate charge issue. "
            "The duplicate transaction will need to be reviewed."
        )
    }


def handle_refund_request(state: SupportState) -> dict:
    message = state.get("processed_message", "").lower()
    active_ref, return_id, order_id = _resolve_entities(state)

    updates = {}
    if active_ref:
        updates["reference_id"] = active_ref
    if return_id:
        updates["return_id"] = return_id
    if order_id:
        updates["order_id"] = order_id

    if active_ref:
        is_order = (active_ref == order_id) or "order" in message or active_ref.startswith(("#ORD", "ORD"))
        entity_name = f"order {active_ref}" if is_order else f"item {active_ref}"
        context_type = "refund" if is_order else "return"

        if any(term in message for term in ("item number", "what was the item", "return item number", "number")):
            if not is_order:
                return {**updates, "response": f"The item number for your return is {active_ref}."}
            else:
                return {**updates, "response": f"The order number for your refund is {active_ref}."}
        elif "status" in message:
            return {**updates, "response": f"The {context_type} status for {entity_name} is currently under review."}

        return {
            **updates,
            "response": (
                f"We identified your {context_type} request for {entity_name}. "
                f"Your {context_type} status is currently under review."
            ),
        }

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
    message = state.get("processed_message", "").lower()

    ESCALATION_SIGNALS = (
        "speak with a human",
        "speak to a human",
        "human agent",
        "live agent",
        "live support",
        "account was compromised",
        "account compromised",
        "compromised",
        "unauthorized charge",
        "unauthorized charges",
        "unauthorized transaction",
        "fraudulent charge",
        "fraud",
    )

    if any(signal in message for signal in ESCALATION_SIGNALS):
        return {
            "escalation_required": True,
            "escalation_reason": "sensitive_request",
        }

    return {
        "response": (
            "Your billing request requires additional review. "
            "Please provide more details about the billing issue."
        )
    }