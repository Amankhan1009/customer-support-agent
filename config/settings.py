import os

from dotenv import load_dotenv


load_dotenv()


CHECKPOINTER_BACKEND = os.getenv(
    "CHECKPOINTER_BACKEND",
    "sqlite",
).lower()

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "support_checkpoints.db",
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
)

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()