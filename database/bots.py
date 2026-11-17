
from database.projects import get_connection


def init_bots_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS managed_bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL UNIQUE,
                username TEXT,

                project_path TEXT NOT NULL,
                venv_path TEXT NOT NULL,
                entry_file TEXT NOT NULL DEFAULT 'main.py',
                log_path TEXT,

                pid INTEGER,
                autostart INTEGER NOT NULL DEFAULT 0
                    CHECK (autostart IN (0, 1)),

                last_started_at TEXT,
                last_stopped_at TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_managed_bots_autostart
            ON managed_bots(autostart)
        """)


def get_all_bots():
    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT *
            FROM managed_bots
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def get_bot(bot_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT *
            FROM managed_bots
            WHERE id = ?
        """, (bot_id,))

        return cursor.fetchone()


def get_autostart_bots():
    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT *
            FROM managed_bots
            WHERE autostart = 1
            ORDER BY id ASC
        """)

        return cursor.fetchall()


def add_bot(
    name,
    username,
    project_path,
    venv_path,
    entry_file="main.py",
    log_path=None
):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO managed_bots (
                name,
                username,
                project_path,
                venv_path,
                entry_file,
                log_path
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            username,
            project_path,
            venv_path,
            entry_file,
            log_path
        ))

        return cursor.lastrowid


def update_bot_pid(bot_id, pid):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE managed_bots
            SET
                pid = ?,
                last_started_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (pid, bot_id))

        return cursor.rowcount > 0


def clear_bot_pid(bot_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE managed_bots
            SET
                pid = NULL,
                last_stopped_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (bot_id,))

        return cursor.rowcount > 0


def set_bot_autostart(bot_id, enabled):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE managed_bots
            SET
                autostart = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (int(bool(enabled)), bot_id))

        return cursor.rowcount > 0


def delete_bot(bot_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            DELETE FROM managed_bots
            WHERE id = ?
        """, (bot_id,))

        return cursor.rowcount > 0
