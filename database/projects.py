import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "portfolio.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_fa TEXT NOT NULL,
                name_en TEXT NOT NULL,
                description_fa TEXT NOT NULL,
                description_en TEXT NOT NULL,
                github_url TEXT NOT NULL,
                bot_url TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def get_active_projects():
    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT *
            FROM projects
            WHERE is_active = 1
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def get_project(project_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT *
            FROM projects
            WHERE id = ? AND is_active = 1
        """, (project_id,))

        return cursor.fetchone()



def add_project(
    name_fa,
    name_en,
    description_fa,
    description_en,
    github_url,
    bot_url
):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO projects (
                name_fa,
                name_en,
                description_fa,
                description_en,
                github_url,
                bot_url
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name_fa,
            name_en,
            description_fa,
            description_en,
            github_url,
            bot_url
        ))

        return cursor.lastrowid


def update_project(
    project_id,
    name_fa,
    name_en,
    description_fa,
    description_en,
    github_url,
    bot_url
):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE projects
            SET
                name_fa = ?,
                name_en = ?,
                description_fa = ?,
                description_en = ?,
                github_url = ?,
                bot_url = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            name_fa,
            name_en,
            description_fa,
            description_en,
            github_url,
            bot_url,
            project_id
        ))

        return cursor.rowcount > 0


def delete_project(project_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            DELETE FROM projects
            WHERE id = ?
        """, (project_id,))

        return cursor.rowcount > 0
