import sqlite3
from datetime import datetime

DB_FILE = "soccer_stats.db"


def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passer_name TEXT,
            passer_role TEXT,
            target_name TEXT,
            target_role TEXT,
            distance REAL,
            angle REAL,
            defender_proximity REAL,
            passer_speed REAL,
            target_speed REAL,
            pass_type TEXT,
            pressure TEXT,
            player_skill REAL,
            prediction TEXT,
            confidence REAL,
            probability REAL,
            timestamp DATETIME
        )
    """)
    conn.commit()
    conn.close()


def save_pass(
    passer_name,
    passer_role,
    target_name,
    target_role,
    distance,
    angle,
    defender_proximity,
    passer_speed,
    target_speed,
    pass_type,
    pressure,
    player_skill,
    prediction,
    confidence,
    probability,
):
    """Saves a pass prediction to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO passes (
            passer_name, passer_role, target_name, target_role, distance, angle,
            defender_proximity, passer_speed, target_speed, pass_type, pressure,
            player_skill, prediction, confidence, probability, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            passer_name,
            passer_role,
            target_name,
            target_role,
            distance,
            angle,
            defender_proximity,
            passer_speed,
            target_speed,
            pass_type,
            pressure,
            player_skill,
            prediction,
            confidence,
            probability,
            datetime.now(),
        ),
    )
    conn.commit()
    conn.close()
