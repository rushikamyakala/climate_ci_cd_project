import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "climate_data.db"

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

APP_NAME = "Climate Intelligence Platform"

LOG_LEVEL = "INFO"

FETCH_INTERVAL = 300