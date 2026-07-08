from langgraph.graph import END, START, StateGraph

from graph.state import SupportState

from nodes.general_nodes import (
    handle_other_general,
    handle_pricing_question,
    handle_product_question,
)

from routers.general_classifier import classify_general_issue
from routers.general_router import route_general_issue


GENERAL_PATH_MAP = {
    "pricing_question": "handle_pricing_question",
    "product_question": "handle_product_question",
    "other_general": "handle_other_general",
}


def build_general_graph():
    builder = StateGraph(SupportState)

    builder.add_node(
        "classify_general_issue",
        classify_general_issue,
    )

    builder.add_node(
        "handle_pricing_question",
        handle_pricing_question,
    )

    builder.add_node(
        "handle_product_question",
        handle_product_question,
    )

    builder.add_node(
        "handle_other_general",
        handle_other_general,
    )

    builder.add_edge(
        START,
        "classify_general_issue",
    )

    builder.add_conditional_edges(
        "classify_general_issue",
        route_general_issue,
        GENERAL_PATH_MAP,
    )

    builder.add_edge("handle_pricing_question", END)
    builder.add_edge("handle_product_question", END)
    builder.add_edge("handle_other_general", END)

    return builder.compile()