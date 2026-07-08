from typing import Literal

from graph.state import SupportState


LLMResultRoute = Literal[
    "continue",
    "error",
]


def route_after_llm_classification(
    state: SupportState,
) -> LLMResultRoute:
    if state.get("error_occurred", False):
        return "error"

    return "continue"