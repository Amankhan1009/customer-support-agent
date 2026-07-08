from graph.state import SupportIntent, SupportState


def route_after_classification(
    state: SupportState,
) -> SupportIntent | str:
    if state["needs_llm_routing"]:
        return "llm"

    return state["intent"]