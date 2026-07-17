import os
import sys
import time
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

from app.database import (
    save_climate_data,
    fetch_last_temperature,
    log_anomaly
)

# -----------------------------
# Load .env properly
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.environ.get("OPENWEATHER_API_KEY")

if not API_KEY:
    logger.error("OpenWeather API Key not found.")

logger.info("Environment loaded successfully.")
logger.info(f"Python Executable: {sys.executable}")

# -----------------------------
# Anomaly Detection Function
# -----------------------------
def detect_anomaly(city: str, current_temp: float) -> bool:
    previous_temp = fetch_last_temperature(city)

    if previous_temp is None:
        logger.info("No previous temperature found.")
        return False

    difference = abs(current_temp - previous_temp)

    if difference > 5:   # threshold
        log_anomaly(city, current_temp, previous_temp)
        logger.warning(f"Anomaly detected in {city}")
        return True

    return False


# -----------------------------
# Main Weather Function
# -----------------------------
def get_weather(city: str) -> dict:
    if not API_KEY:
        return {"error": "API key not found"}

    start_total = time.time()

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    start_api = time.time()
    response = requests.get(url, timeout=10)
    api_response_time = round(time.time() - start_api, 3)

    if response.status_code != 200:
        logger.error(f"Weather API failed for {city}")
        return {"error": "Invalid API key or city name"}

    data = response.json()

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    # Save to DB
    save_climate_data(city, temperature, humidity, wind_speed)
    logger.info(f"Weather data stored for {city}")

    # Detect anomaly
    anomaly = detect_anomaly(city, temperature)

    total_execution_time = round(time.time() - start_total, 3)
    logger.info(
    f"Weather fetched successfully for {city} "
    f"in {total_execution_time} seconds."
)
    return {
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "is_anomaly": anomaly,
        "api_response_time": api_response_time,
        "total_execution_time": total_execution_time
    }