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

# ── JWT authentication ────────────────────────────────────────────────────────

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "insecure-default-change-in-production",
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

# ── Default admin user (seeded on first startup) ──────────────────────────────

DEFAULT_ADMIN_USERNAME = os.getenv(
    "DEFAULT_ADMIN_USERNAME",
    "admin",
)

DEFAULT_ADMIN_PASSWORD = os.getenv(
    "DEFAULT_ADMIN_PASSWORD",
    "admin123",
)