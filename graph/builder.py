from langgraph.graph import END, START, StateGraph

from graph.state import SupportState

from nodes.error_nodes import handle_workflow_error
from nodes.human_support_nodes import human_support_workflow
from nodes.specialized_nodes import fallback_support
from nodes.support_nodes import (
    finalize_response,
    receive_query,
)

from routers.classification_router import route_after_classification
from routers.error_router import route_after_llm_classification
from routers.escalation_router import route_after_support_workflow
from routers.intent_classifier import classify_intent
from routers.intent_router import (
    route_by_intent,
    route_llm_intent_node,
)
from routers.llm_classifier import llm_classify_intent

from workflows.account.builder import build_account_graph
from workflows.billing.builder import build_billing_graph
from workflows.general.builder import build_general_graph
from workflows.technical.builder import build_technical_graph


INTENT_PATH_MAP = {
    "billing": "billing_workflow",
    "technical": "technical_workflow",
    "account": "account_workflow",
    "general": "general_workflow",
    "unknown": "fallback_support",
}


def build_graph(checkpointer=None):
    builder = StateGraph(SupportState)

    # --------------------------------------------------
    # Build specialized subgraphs
    # --------------------------------------------------

    billing_graph = build_billing_graph()
    technical_graph = build_technical_graph()
    account_graph = build_account_graph()
    general_graph = build_general_graph()

    # --------------------------------------------------
    # Input processing
    # --------------------------------------------------

    builder.add_node(
        "receive_query",
        receive_query,
    )

    # --------------------------------------------------
    # Top-level intent classification
    # --------------------------------------------------

    builder.add_node(
        "classify_intent",
        classify_intent,
    )

    builder.add_node(
        "llm_classify_intent",
        llm_classify_intent,
    )

    # --------------------------------------------------
    # LLM routing bridge
    # --------------------------------------------------

    builder.add_node(
        "route_llm_intent",
        route_llm_intent_node,
    )

    # --------------------------------------------------
    # Specialized support workflows
    # --------------------------------------------------

    builder.add_node(
        "billing_workflow",
        billing_graph,
    )

    builder.add_node(
        "technical_workflow",
        technical_graph,
    )

    builder.add_node(
        "account_workflow",
        account_graph,
    )

    builder.add_node(
        "general_workflow",
        general_graph,
    )

    # --------------------------------------------------
    # Fallback support
    # --------------------------------------------------

    builder.add_node(
        "fallback_support",
        fallback_support,
    )

    # --------------------------------------------------
    # Error handling
    # --------------------------------------------------

    builder.add_node(
        "handle_workflow_error",
        handle_workflow_error,
    )

    # --------------------------------------------------
    # Human escalation workflow
    # --------------------------------------------------

    builder.add_node(
        "human_support_workflow",
        human_support_workflow,
    )

    # --------------------------------------------------
    # Final response processing
    # --------------------------------------------------

    builder.add_node(
        "finalize_response",
        finalize_response,
    )

    # --------------------------------------------------
    # Entry path
    # --------------------------------------------------

    builder.add_edge(
        START,
        "receive_query",
    )

    builder.add_edge(
        "receive_query",
        "classify_intent",
    )

    # --------------------------------------------------
    # Hybrid intent routing
    # --------------------------------------------------

    builder.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "billing": "billing_workflow",
            "technical": "technical_workflow",
            "account": "account_workflow",
            "general": "general_workflow",
            "unknown": "fallback_support",
            "llm": "llm_classify_intent",
        },
    )

    # --------------------------------------------------
    # LLM result routing
    # --------------------------------------------------

    # First decision:
    # Did the LLM classifier execute successfully?
    builder.add_conditional_edges(
        "llm_classify_intent",
        route_after_llm_classification,
        {
            "continue": "route_llm_intent",
            "error": "handle_workflow_error",
        },
    )

    # Second decision:
    # Which support domain did the LLM classify?
    builder.add_conditional_edges(
        "route_llm_intent",
        route_by_intent,
        INTENT_PATH_MAP,
    )

    # --------------------------------------------------
    # Post-workflow routing
    # --------------------------------------------------

    # Billing currently completes directly.
    builder.add_edge(
        "billing_workflow",
        "finalize_response",
    )

    # Technical workflow may finalize or escalate.
    builder.add_conditional_edges(
        "technical_workflow",
        route_after_support_workflow,
        {
            "finalize": "finalize_response",
            "escalate": "human_support_workflow",
        },
    )

    # Account workflow may finalize or escalate.
    builder.add_conditional_edges(
        "account_workflow",
        route_after_support_workflow,
        {
            "finalize": "finalize_response",
            "escalate": "human_support_workflow",
        },
    )

    # General workflow completes directly.
    builder.add_edge(
        "general_workflow",
        "finalize_response",
    )

    # Unsupported requests complete through fallback.
    builder.add_edge(
        "fallback_support",
        "finalize_response",
    )

    # --------------------------------------------------
    # Error escalation
    # --------------------------------------------------

    builder.add_edge(
        "handle_workflow_error",
        "human_support_workflow",
    )

    # Human escalation rejoins common finalization.
    builder.add_edge(
        "human_support_workflow",
        "finalize_response",
    )

    # --------------------------------------------------
    # Graph completion
    # --------------------------------------------------

    builder.add_edge(
        "finalize_response",
        END,
    )

    return builder.compile(checkpointer=checkpointer)