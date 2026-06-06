import sqlite3
from pathlib import Path


DB_PATH = "memory/weather_memory.db"


def init_db() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                favorite_city TEXT,
                last_city TEXT,
                temp_unit TEXT DEFAULT 'celsius',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                intent TEXT DEFAULT '',
                city TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
            """
        )


def save_preference(
    user_id: str,
    favorite_city: str | None = None,
    last_city: str | None = None,
    temp_unit: str | None = None,
) -> None:
    current = get_preference(user_id)
    next_favorite = favorite_city if favorite_city is not None else current["favorite_city"]
    next_last = last_city if last_city is not None else current["last_city"]
    next_unit = temp_unit if temp_unit is not None else current["temp_unit"]

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, favorite_city, last_city, temp_unit)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                favorite_city = excluded.favorite_city,
                last_city = excluded.last_city,
                temp_unit = excluded.temp_unit,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, next_favorite, next_last, next_unit),
        )


def get_preference(user_id: str) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT favorite_city, last_city, temp_unit
            FROM user_preferences
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if not row:
        return {"favorite_city": "", "last_city": "", "temp_unit": "celsius"}
    return {
        "favorite_city": row["favorite_city"] or "",
        "last_city": row["last_city"] or "",
        "temp_unit": row["temp_unit"] or "celsius",
    }


def save_message(
    user_id: str,
    role: str,
    content: str,
    intent: str = "",
    city: str = "",
) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO conversation_history (user_id, role, content, intent, city)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, role, content, intent, city),
        )


def get_recent_messages(user_id: str, limit: int = 6) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT role, content, intent, city, created_at
            FROM conversation_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    return [
        {
            "role": row["role"],
            "content": row["content"],
            "intent": row["intent"],
            "city": row["city"],
            "created_at": row["created_at"],
        }
        for row in reversed(rows)
    ]


def clear_conversation(user_id: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))


def upsert_session(user_id: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT id
            FROM user_sessions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
        if row:
            conn.execute(
                """
                UPDATE user_sessions
                SET last_active = CURRENT_TIMESTAMP,
                    message_count = message_count + 1
                WHERE id = ?
                """,
                (row[0],),
            )
        else:
            conn.execute(
                """
                INSERT INTO user_sessions (user_id, message_count)
                VALUES (?, 1)
                """,
                (user_id,),
            )


def get_session_stats(user_id: str) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT session_start, last_active, message_count
            FROM user_sessions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    if not row:
        return {"session_start": "", "last_active": "", "message_count": 0}
    return {
        "session_start": row["session_start"],
        "last_active": row["last_active"],
        "message_count": row["message_count"],
    }


init_db()
