from typing import Literal

from graph.state import SupportState


PostWorkflowRoute = Literal[
    "finalize",
    "escalate",
]


def route_after_support_workflow(
    state: SupportState,
) -> PostWorkflowRoute:
    if state.get("escalation_required", False):
        return "escalate"

    return "finalize"