from typing import Literal

from graph.state import SupportState


GeneralIssue = Literal[
    "pricing_question",
    "product_question",
    "other_general",
]


def route_general_issue(state: SupportState) -> GeneralIssue:
    return state["general_issue"]