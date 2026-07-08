from graph.state import BillingIssue, SupportState


def route_billing_issue(state: SupportState) -> BillingIssue:
    return state["billing_issue"]