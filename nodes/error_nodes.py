import logging

from graph.state import SupportState


logger = logging.getLogger(__name__)


def handle_workflow_error(state: SupportState) -> dict:
    error_type = state.get(
        "error_type",
        "unexpected_error",
    )

    error_message = state.get(
        "error_message",
        "No error details available.",
    )

    logger.error(
        "Support workflow failed. type=%s message=%s",
        error_type,
        error_message,
    )

    return {
        "response": (
            "We encountered an unexpected problem while processing "
            "your request. Your request has been forwarded for "
            "additional support review."
        ),
        "escalation_required": True,
        "escalation_reason": "unsupported_request",
    }