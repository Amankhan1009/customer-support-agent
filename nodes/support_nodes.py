from langchain_core.messages import AIMessage, HumanMessage

from graph.state import SupportState


def receive_query(state: SupportState) -> dict:
    customer_message = state["customer_message"].strip()

    return {
        "processed_message": customer_message,
        "messages": [
            HumanMessage(content=customer_message)
        ],
    }


def finalize_response(state: SupportState) -> dict:
    response = state["response"]

    return {
        "response": response,
        "messages": [
            AIMessage(content=response)
        ],
    }