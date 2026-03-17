import sqlite3
from datetime import datetime

DB_PATH = "community_votes.db"


def get_connection():
    return sqlite3.connect(DB_PATH)

def clear_all_votes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM votes")
    cursor.execute("DELETE FROM submissions")

    conn.commit()
    conn.close()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submitted_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            round_index INTEGER NOT NULL,
            left_weapon_id INTEGER NOT NULL,
            right_weapon_id INTEGER NOT NULL,
            winner_weapon_id INTEGER NOT NULL,
            loser_weapon_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(id)
        )
        """
    )

    conn.commit()
    conn.close()


def save_submission(vote_history):
    """
    vote_history: list[dict]
    每条格式示例：
    {
        "round_index": 1,
        "left_weapon_id": 1001,
        "right_weapon_id": 2004,
        "winner_weapon_id": 1001,
        "loser_weapon_id": 2004,
    }
    """
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()

    cursor.execute(
        "INSERT INTO submissions (submitted_at) VALUES (?)",
        (now,),
    )
    submission_id = cursor.lastrowid

    for row in vote_history:
        cursor.execute(
            """
            INSERT INTO votes (
                submission_id,
                round_index,
                left_weapon_id,
                right_weapon_id,
                winner_weapon_id,
                loser_weapon_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                submission_id,
                row["round_index"],
                row["left_weapon_id"],
                row["right_weapon_id"],
                row["winner_weapon_id"],
                row["loser_weapon_id"],
                now,
            ),
        )

    conn.commit()
    conn.close()


def get_community_leaderboard():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        WITH appearances AS (
            SELECT left_weapon_id AS weapon_id FROM votes
            UNION ALL
            SELECT right_weapon_id AS weapon_id FROM votes
        ),
        appearance_counts AS (
            SELECT weapon_id, COUNT(*) AS appearances
            FROM appearances
            GROUP BY weapon_id
        ),
        win_counts AS (
            SELECT winner_weapon_id AS weapon_id, COUNT(*) AS wins
            FROM votes
            GROUP BY winner_weapon_id
        )
        SELECT
            a.weapon_id,
            COALESCE(w.wins, 0) AS wins,
            a.appearances,
            ROUND(
                COALESCE(w.wins, 0) * 100.0 / a.appearances,
                1
            ) AS win_rate
        FROM appearance_counts a
        LEFT JOIN win_counts w
            ON a.weapon_id = w.weapon_id
        ORDER BY wins DESC, win_rate DESC, appearances DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return rows