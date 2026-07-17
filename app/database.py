# app/database.py
import sqlite3
import logging
from datetime import datetime
from app.config import DB_NAME

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def init_db() -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS climate_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            timestamp TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            previous_temperature REAL,
            difference REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    logger.info("Database initialized successfully.")
    conn.close()


def save_climate_data(
    city: str,
    temp: float,
    humidity: float,
    wind: float
) -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO climate_data (city, temperature, humidity, wind_speed, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (city, temp, humidity, wind, timestamp))

    conn.commit()
    logger.info(f"Climate data saved for {city}")
    conn.close()


def fetch_last_temperature(city: str) -> float | None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT temperature FROM climate_data
        WHERE city = ?
        ORDER BY id DESC LIMIT 1
    """, (city,))

    result = cursor.fetchone()
    logger.info(f"Fetched latest temperature for {city}")
    conn.close()

    return result[0] if result else None


def log_anomaly(
    city: str,
    current_temp: float,
    previous_temp: float
) -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    difference = abs(current_temp - previous_temp)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO anomalies (city, temperature, previous_temperature, difference, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (city, current_temp, previous_temp, difference, timestamp))

    conn.commit()
    logger.warning(f"Temperature anomaly detected in {city}")
    conn.close()


def get_all_records() -> list:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, city, temperature, humidity, wind_speed, timestamp
        FROM climate_data
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    conn.close()

    return records
logger.info("Fetched all climate records.")


def get_anomalies() -> list:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, city, temperature, previous_temperature, difference, timestamp
        FROM anomalies
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    conn.close()
    return records
logger.info("Fetched anomaly records.")


def get_last_7_records(city: str) -> list:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT temperature, timestamp
        FROM climate_data
        WHERE city = ?
        ORDER BY id DESC
        LIMIT 7
    """, (city,))

    records = cursor.fetchall()
    conn.close()
    return records
    logger.info(f"Fetched last 7 records for {city}")