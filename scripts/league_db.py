import json
import sqlite3
from datetime import datetime
from typing import Dict


class LeagueDB:
    """
    SQL-backed match history and analytics for ULTRA Phase 3.
    """

    def __init__(self, db_path: str = "league_meta.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                team_blue_score INTEGER,
                team_red_score INTEGER,
                spectacle_avg REAL,
                meta_json TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                player_id TEXT PRIMARY KEY,
                goals INTEGER,
                wins INTEGER,
                elo REAL
            )
        """)
        self.conn.commit()

    def log_match(self, blue_score: int, red_score: int, spectacle: float, metadata: Dict):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO matches (timestamp, team_blue_score, team_red_score, spectacle_avg, meta_json)
            VALUES (?, ?, ?, ?, ?)
        """,
            (datetime.now().isoformat(), blue_score, red_score, spectacle, json.dumps(metadata)),
        )
        self.conn.commit()

    def get_hall_of_fame(self, limit: int = 10):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM player_stats ORDER BY elo DESC LIMIT ?", (limit,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()
