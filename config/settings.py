import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "support_checkpoints.db",
)

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()