import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from graph.builder import build_graph

from config.logging import configure_logging
from config.settings import DATABASE_PATH

DATABASE_PATH = "support_checkpoints.db"


def main():

    configure_logging()
    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(connection)
    graph = build_graph(checkpointer=checkpointer)

    thread_id = input("Conversation ID: ").strip()

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    snapshot = graph.get_state(config)

    if snapshot.interrupts:
        interrupt_data = snapshot.interrupts[0].value

        print("\n--- Pending Human Review ---")
        print("Customer Message:", interrupt_data.get("customer_message"))
        print("Intent:", interrupt_data.get("intent"))
        print("Escalation Reason:", interrupt_data.get("escalation_reason"))

        human_response = input("\nHuman Support Response: ").strip()

        result = graph.invoke(
            Command(resume=human_response),
            config=config,
        )

        print("\nSupport Agent:", result["response"])

    else:
        customer_message = input("Customer: ").strip()

        initial_state = {
            "customer_message": customer_message,
        }

        result = graph.invoke(
            initial_state,
            config=config,
        )

        snapshot = graph.get_state(config)

        if snapshot.interrupts:
            interrupt_data = snapshot.interrupts[0].value

            print("\n--- Human Review Required ---")
            print("Customer Message:", interrupt_data.get("customer_message"))
            print("Intent:", interrupt_data.get("intent"))
            print("Escalation Reason:", interrupt_data.get("escalation_reason"))
            print(
                "\nRun the application again with the same Conversation ID "
                "to provide the human support response."
            )

        else:
            print("\nSupport Agent:", result["response"])

    connection.close()


if __name__ == "__main__":
    main()