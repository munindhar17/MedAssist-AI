import sqlite3
from datetime import datetime
from pathlib import Path

DB_NAME = Path(__file__).resolve().parents[2] / "predictions.db"
PREDICTION_VERSION = "v3"


def get_connection():

    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptoms TEXT,
            disease TEXT,
            confidence TEXT,
            severity INTEGER,
            risk TEXT,
            time TEXT,
            prediction_version TEXT DEFAULT 'v1'
        )
        """
    )

    cursor.execute("PRAGMA table_info(history)")
    columns = [row[1] for row in cursor.fetchall()]

    if "prediction_version" not in columns:
        cursor.execute(
            """
            ALTER TABLE history
            ADD COLUMN prediction_version TEXT DEFAULT 'v1'
            """
        )

    conn.commit()

    conn.close()


initialize_database()


def save_prediction(
    symptoms,
    disease,
    confidence,
    severity,
    risk,
    prediction_version=PREDICTION_VERSION
):

    current_time = datetime.now().strftime(
        "%d-%b-%Y %I:%M %p"
    )

    conn = get_connection()

    cursor = conn.cursor()

    current_symptoms = ",".join(
        sorted(symptoms)
    )

    cursor.execute(
        """
        INSERT INTO history(
            symptoms,
            disease,
            confidence,
            severity,
            risk,
            time,
            prediction_version
        )

        VALUES(
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """,

        (
            current_symptoms,
            disease,
            confidence,
            severity,
            risk,
            current_time,
            prediction_version
        )
    )

    conn.commit()

    conn.close()


def get_history():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM history
        WHERE prediction_version = ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (PREDICTION_VERSION,)
    )

    result = cursor.fetchall()

    conn.close()

    return result


def get_all_history():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM history
        WHERE prediction_version = ?
        ORDER BY id DESC
        """,
        (PREDICTION_VERSION,)
    )

    result = cursor.fetchall()

    conn.close()

    return result
