from graph.state import AccountIssue, SupportState


def route_account_issue(state: SupportState) -> AccountIssue:
    return state["account_issue"]