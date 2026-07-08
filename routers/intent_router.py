from graph.state import SupportIntent, SupportState


def route_by_intent(state: SupportState) -> SupportIntent:
    return state["intent"]


def route_llm_intent_node(state: SupportState) -> dict:
    return {}