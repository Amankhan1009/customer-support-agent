import sqlite3

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.sqlite import SqliteSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

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

        pool = ConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=5,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
                "row_factory": dict_row,
            },
            open=True,
        )

        pool.wait()

        checkpointer = PostgresSaver(pool)

        # Creates the required PostgreSQL checkpoint tables.
        checkpointer.setup()

        return checkpointer, pool

    raise ValueError(
        f"Unsupported CHECKPOINTER_BACKEND: "
        f"{CHECKPOINTER_BACKEND}"
    )


def close_checkpointer(resource):
    resource.close()