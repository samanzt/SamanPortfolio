
from database.projects import get_connection


ALLOWED_EVENTS = {
    "start",
    "projects_list",
    "project_details",
    "github_click",
    "bot_click"
}


def init_stats_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS bot_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                project_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_bot_events_type
            ON bot_events(event_type)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_bot_events_user
            ON bot_events(user_id)
        """)


def track_event(user, event_type, project_id=None):
    if user is None or event_type not in ALLOWED_EVENTS:
        return

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO bot_events (
                user_id,
                event_type,
                project_id
            )
            VALUES (?, ?, ?)
        """, (
            user.id,
            event_type,
            project_id
        ))


def get_statistics():
    with get_connection() as connection:
        row = connection.execute("""
            SELECT
                COUNT(DISTINCT user_id) AS unique_users,

                SUM(CASE
                    WHEN event_type = 'start' THEN 1
                    ELSE 0
                END) AS start_count,

                SUM(CASE
                    WHEN event_type = 'projects_list' THEN 1
                    ELSE 0
                END) AS projects_list_views,

                SUM(CASE
                    WHEN event_type = 'project_details' THEN 1
                    ELSE 0
                END) AS project_details_views,

                SUM(CASE
                    WHEN event_type = 'github_click' THEN 1
                    ELSE 0
                END) AS github_clicks,

                SUM(CASE
                    WHEN event_type = 'bot_click' THEN 1
                    ELSE 0
                END) AS bot_clicks

            FROM bot_events
        """).fetchone()

    return {
        "unique_users": row["unique_users"] or 0,
        "start_count": row["start_count"] or 0,
        "projects_list_views": row["projects_list_views"] or 0,
        "project_details_views": row["project_details_views"] or 0,
        "github_clicks": row["github_clicks"] or 0,
        "bot_clicks": row["bot_clicks"] or 0
    }
