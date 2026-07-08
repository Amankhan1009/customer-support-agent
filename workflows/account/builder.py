from langgraph.graph import END, START, StateGraph

from graph.state import SupportState

from nodes.account_nodes import (
    handle_account_deletion,
    handle_account_management,
    handle_login_problem,
    handle_other_account,
    handle_password_reset,
    handle_suspicious_access,
)

from routers.account_classifier import classify_account_issue
from routers.account_router import route_account_issue


ACCOUNT_PATH_MAP = {
    "login_problem": "handle_login_problem",
    "password_reset": "handle_password_reset",
    "account_management": "handle_account_management",
    "suspicious_access": "handle_suspicious_access",
    "account_deletion": "handle_account_deletion",
    "other_account": "handle_other_account",
}


def build_account_graph():
    builder = StateGraph(SupportState)

    builder.add_node(
        "classify_account_issue",
        classify_account_issue,
    )

    builder.add_node(
        "handle_login_problem",
        handle_login_problem,
    )

    builder.add_node(
        "handle_password_reset",
        handle_password_reset,
    )

    builder.add_node(
        "handle_account_management",
        handle_account_management,
    )

    builder.add_node(
        "handle_suspicious_access",
        handle_suspicious_access,
    )

    builder.add_node(
        "handle_account_deletion",
        handle_account_deletion,
    )

    builder.add_node(
        "handle_other_account",
        handle_other_account,
    )

    builder.add_edge(
        START,
        "classify_account_issue",
    )

    builder.add_conditional_edges(
        "classify_account_issue",
        route_account_issue,
        ACCOUNT_PATH_MAP,
    )

    builder.add_edge("handle_login_problem", END)
    builder.add_edge("handle_password_reset", END)
    builder.add_edge("handle_account_management", END)
    builder.add_edge("handle_suspicious_access", END)
    builder.add_edge("handle_account_deletion", END)
    builder.add_edge("handle_other_account", END)

    return builder.compile()