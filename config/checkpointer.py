import sqlite3

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.sqlite import SqliteSaver

from config.settings import (
    CHECKPOINTER_BACKEND,
    DATABASE_PATH,
    DATABASE_URL,
)


def create_checkpointer():
    if CHECKPOINTER_BACKEND == "sqlite":
        connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False,
        )

        checkpointer = SqliteSaver(connection)

        return checkpointer, connection

    if CHECKPOINTER_BACKEND == "postgres":
        if not DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is required when "
                "CHECKPOINTER_BACKEND=postgres."
            )

        checkpointer_context = PostgresSaver.from_conn_string(
            DATABASE_URL
        )

        checkpointer = checkpointer_context.__enter__()

        # Creates the required PostgreSQL checkpoint tables.
        checkpointer.setup()

        return checkpointer, checkpointer_context

    raise ValueError(
        f"Unsupported CHECKPOINTER_BACKEND: "
        f"{CHECKPOINTER_BACKEND}"
    )


def close_checkpointer(resource):
    if CHECKPOINTER_BACKEND == "sqlite":
        resource.close()
        return

    if CHECKPOINTER_BACKEND == "postgres":
        resource.__exit__(None, None, None)