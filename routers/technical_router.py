from graph.state import (
    ResolutionStatus,
    SupportState,
    TechnicalIssue,
)


def route_technical_issue(
    state: SupportState,
) -> TechnicalIssue:
    return state["technical_issue"]


def route_resolution(
    state: SupportState,
) -> ResolutionStatus:
    return state["resolution_status"]