import bcrypt
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

import config.settings as settings

security = HTTPBearer()


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8"),
    )


# ── User database ─────────────────────────────────────────────────────────────

def init_user_db() -> None:
    """
    Creates users and user_threads tables in the same database
    as the checkpointer and seeds the default admin user.
    """
    if settings.CHECKPOINTER_BACKEND == "sqlite":
        conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    username         TEXT UNIQUE NOT NULL,
                    hashed_password  TEXT NOT NULL,
                    created_at       TEXT DEFAULT (datetime('now'))
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_threads (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    username    TEXT NOT NULL,
                    thread_id   TEXT UNIQUE NOT NULL,
                    title       TEXT NOT NULL,
                    updated_at  TEXT DEFAULT (datetime('now'))
                )
                """
            )
            conn.commit()

            conn.execute(
                """
                INSERT INTO users (username, hashed_password) VALUES (?, ?)
                ON CONFLICT(username) DO UPDATE SET hashed_password = excluded.hashed_password
                """,
                (settings.DEFAULT_ADMIN_USERNAME, hash_password(settings.DEFAULT_ADMIN_PASSWORD)),
            )
            conn.commit()
        finally:
            conn.close()

    elif settings.CHECKPOINTER_BACKEND == "postgres":
        import psycopg

        with psycopg.connect(settings.DATABASE_URL, autocommit=True) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id               SERIAL PRIMARY KEY,
                    username         VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password  TEXT NOT NULL,
                    created_at       TIMESTAMP DEFAULT NOW()
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_threads (
                    id          SERIAL PRIMARY KEY,
                    username    VARCHAR(255) NOT NULL,
                    thread_id   VARCHAR(255) UNIQUE NOT NULL,
                    title       TEXT NOT NULL,
                    updated_at  TIMESTAMP DEFAULT NOW()
                )
                """
            )
            conn.execute(
                """
                INSERT INTO users (username, hashed_password) VALUES (%s, %s)
                ON CONFLICT(username) DO UPDATE SET hashed_password = EXCLUDED.hashed_password
                """,
                (settings.DEFAULT_ADMIN_USERNAME, hash_password(settings.DEFAULT_ADMIN_PASSWORD)),
            )


def save_user_thread(username: str, thread_id: str, title: str | None = None) -> None:
    clean_title = title.strip()[:50] if title else "Conversation"
    if settings.CHECKPOINTER_BACKEND == "sqlite":
        conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute(
                """
                INSERT INTO user_threads (username, thread_id, title, updated_at)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(thread_id) DO UPDATE SET updated_at = datetime('now')
                """,
                (username, thread_id, clean_title),
            )
            conn.commit()
        finally:
            conn.close()
    elif settings.CHECKPOINTER_BACKEND == "postgres":
        import psycopg
        with psycopg.connect(settings.DATABASE_URL, autocommit=True) as conn:
            conn.execute(
                """
                INSERT INTO user_threads (username, thread_id, title, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT(thread_id) DO UPDATE SET updated_at = NOW()
                """,
                (username, thread_id, clean_title),
            )


def get_user_threads(username: str) -> list[dict]:
    if settings.CHECKPOINTER_BACKEND == "sqlite":
        conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
        try:
            conn.row_factory = sqlite3.Row
            # Auto-sync any existing checkpoints for this user into user_threads
            prefix = f"customer-{username}%"
            cp_rows = conn.execute(
                "SELECT DISTINCT thread_id FROM checkpoints WHERE thread_id LIKE ?",
                (prefix,),
            ).fetchall()
            for r in cp_rows:
                tid = r["thread_id"]
                conn.execute(
                    """
                    INSERT INTO user_threads (username, thread_id, title, updated_at)
                    VALUES (?, ?, 'Conversation', datetime('now'))
                    ON CONFLICT(thread_id) DO NOTHING
                    """,
                    (username, tid),
                )
            conn.commit()

            rows = conn.execute(
                """
                SELECT thread_id, title, updated_at
                FROM user_threads
                WHERE username = ?
                ORDER BY updated_at DESC
                """,
                (username,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
    elif settings.CHECKPOINTER_BACKEND == "postgres":
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(settings.DATABASE_URL, row_factory=dict_row) as conn:
            prefix = f"customer-{username}%"
            cp_rows = conn.execute(
                "SELECT DISTINCT thread_id FROM checkpoints WHERE thread_id LIKE %s",
                (prefix,),
            ).fetchall()
            for r in cp_rows:
                tid = r["thread_id"]
                conn.execute(
                    """
                    INSERT INTO user_threads (username, thread_id, title, updated_at)
                    VALUES (%s, %s, 'Conversation', NOW())
                    ON CONFLICT(thread_id) DO NOTHING
                    """,
                    (username, tid),
                )
            return conn.execute(
                """
                SELECT thread_id, title, TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI:SS') as updated_at
                FROM user_threads
                WHERE username = %s
                ORDER BY updated_at DESC
                """,
                (username,),
            ).fetchall()
    return []


def get_user(username: str) -> Optional[dict]:
    """Returns the user record for the given username, or None if not found."""
    if settings.CHECKPOINTER_BACKEND == "sqlite":
        conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
        try:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT username, hashed_password FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    elif settings.CHECKPOINTER_BACKEND == "postgres":
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(settings.DATABASE_URL, row_factory=dict_row) as conn:
            return conn.execute(
                "SELECT username, hashed_password FROM users WHERE username = %s",
                (username,),
            ).fetchone()

    return None

def create_user(username: str, password: str) -> dict:
    hashed = hash_password(password)
    if settings.CHECKPOINTER_BACKEND == "sqlite":
        conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute(
                "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
                (username, hashed),
            )
            conn.commit()
        finally:
            conn.close()
    elif settings.CHECKPOINTER_BACKEND == "postgres":
        import psycopg
        with psycopg.connect(settings.DATABASE_URL, autocommit=True) as conn:
            conn.execute(
                "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
                (username, hashed),
            )
    return {"username": username}

# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency injected into protected endpoints.
    Validates the Bearer JWT and returns {"username": ...}.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )