from langgraph.types import interrupt

from graph.state import SupportState


def human_support_workflow(state: SupportState) -> dict:
    human_decision = interrupt(
        {
            "type": "human_support_review",
            "customer_message": state.get("processed_message", ""),
            "intent": state.get("intent", "unknown"),
            "escalation_reason": state.get(
                "escalation_reason",
                "unsupported_request",
            ),
            "diagnostic_result": state.get("diagnostic_result"),
        }
    )

    return {
        "response": str(human_decision),
        "escalation_required": False,
    }