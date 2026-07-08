from langgraph.graph import StateGraph, START, END

from graph.state import SupportState

from nodes.technical_nodes import (
    diagnose_application_error,
    diagnose_performance_issue,
    diagnose_feature_issue,
    diagnose_other_technical,
    prepare_technical_response,
    mark_for_escalation,
)

from routers.technical_classifier import classify_technical_issue
from routers.technical_router import (
    route_technical_issue,
    route_resolution,
)


TECHNICAL_PATH_MAP = {
    "application_error": "diagnose_application_error",
    "performance_issue": "diagnose_performance_issue",
    "feature_issue": "diagnose_feature_issue",
    "other_technical": "diagnose_other_technical",
}


RESOLUTION_PATH_MAP = {
    "resolved": "prepare_technical_response",
    "unresolved": "mark_for_escalation",
}


def build_technical_graph():
    builder = StateGraph(SupportState)

    # Technical issue classification
    builder.add_node(
        "classify_technical_issue",
        classify_technical_issue,
    )

    # Diagnostic nodes
    builder.add_node(
        "diagnose_application_error",
        diagnose_application_error,
    )

    builder.add_node(
        "diagnose_performance_issue",
        diagnose_performance_issue,
    )

    builder.add_node(
        "diagnose_feature_issue",
        diagnose_feature_issue,
    )

    builder.add_node(
        "diagnose_other_technical",
        diagnose_other_technical,
    )

    # Resolution nodes
    builder.add_node(
        "prepare_technical_response",
        prepare_technical_response,
    )

    builder.add_node(
        "mark_for_escalation",
        mark_for_escalation,
    )

    # Entry
    builder.add_edge(
        START,
        "classify_technical_issue",
    )

    # Conditional routing decision 1:
    # select the appropriate diagnostic node.
    builder.add_conditional_edges(
        "classify_technical_issue",
        route_technical_issue,
        TECHNICAL_PATH_MAP,
    )

    # Conditional routing decision 2:
    # evaluate the result of each diagnostic path.
    builder.add_conditional_edges(
        "diagnose_application_error",
        route_resolution,
        RESOLUTION_PATH_MAP,
    )

    builder.add_conditional_edges(
        "diagnose_performance_issue",
        route_resolution,
        RESOLUTION_PATH_MAP,
    )

    builder.add_conditional_edges(
        "diagnose_feature_issue",
        route_resolution,
        RESOLUTION_PATH_MAP,
    )

    builder.add_conditional_edges(
        "diagnose_other_technical",
        route_resolution,
        RESOLUTION_PATH_MAP,
    )

    # Workflow completion
    builder.add_edge(
        "prepare_technical_response",
        END,
    )

    builder.add_edge(
        "mark_for_escalation",
        END,
    )

    return builder.compile()