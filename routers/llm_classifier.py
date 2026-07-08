from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm
from graph.state import SupportState
from schemas.routing import IntentClassification


CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an intent classifier for a customer support system.

Classify the latest customer message into exactly one category:

billing:
Payment issues, charges, refunds, invoices, subscription charges,
or other billing-related problems.

technical:
Application errors, crashes, bugs, broken functionality,
or other technical problems.

account:
Login problems, passwords, account access, profile access,
or account management issues.

general:
Product features, pricing information, product information,
or general questions about the service.

unknown:
Requests that do not belong to any supported category.

Use previous conversation context only when the latest customer
message is ambiguous or refers to an earlier issue.

Prioritize the latest customer message over older conversation history.

Return only the structured classification result.
""",
        ),
        (
            "human",
            """
Conversation context:
{conversation_context}

Latest customer message:
{customer_message}
""",
        ),
    ]
)


def build_conversation_context(state: SupportState) -> str:
    messages = state.get("messages", [])

    # Exclude the latest HumanMessage because receive_query()
    # already added it to messages and we pass it separately below.
    previous_messages = messages[:-1]

    if not previous_messages:
        return "No previous conversation context."

    recent_messages = previous_messages[-6:]

    return "\n".join(
        f"{message.type}: {message.content}"
        for message in recent_messages
    )


def llm_classify_intent(state: SupportState) -> dict:
    try:
        llm = get_llm()

        structured_llm = llm.with_structured_output(
            IntentClassification
        )

        chain = CLASSIFICATION_PROMPT | structured_llm

        result = chain.invoke(
            {
                "customer_message": state["processed_message"],
                "conversation_context": build_conversation_context(state),
            }
        )

        return {
            "intent": result.intent,
            "routing_source": "llm",
            "needs_llm_routing": False,
            "error_occurred": False,
        }

    except Exception as exc:
        return {
            "intent": "unknown",
            "routing_source": "unresolved",
            "needs_llm_routing": False,
            "error_occurred": True,
            "error_type": "llm_routing_error",
            "error_message": str(exc),
        }