import pytest
from app.climate_api import get_weather
from app.database import save_climate_data, fetch_last_temperature
from app.anomaly_detection import detect_anomaly

# ---------- API TESTS ----------

def test_api_response():
    data = get_weather("Bangalore")

    assert "temperature" in data
    assert "humidity" in data
    assert "wind_speed" in data

# ---------- DATA VALIDATION ----------

def test_temperature_range():
    data = get_weather("Bangalore")

    temp = data["temperature"]

    assert -50 <= temp <= 60

def test_humidity_range():
    data = get_weather("Bangalore")

    humidity = data["humidity"]

    assert 0 <= humidity <= 100

# ---------- DATABASE TESTS ----------

def test_database_insert():
    save_climate_data("TestCity", 25.0, 60, 5)
    result = fetch_last_temperature("TestCity")
    assert result == 25.0

# ---------- ANOMALY DETECTION ----------

def test_anomaly_detection():
    city = "TestCity"

    save_climate_data(city, 20, 50, 5)
    is_anomaly = detect_anomaly(city, 40)

    assert is_anomaly is True
def test_api_response_time():
    data = get_weather("Bangalore")

    assert data["api_response_time"] >= 0
def test_total_execution_time():
    data = get_weather("Bangalore")

    assert data["total_execution_time"] >= 0
def test_weather_data_type():
    data = get_weather("Bangalore")

    assert isinstance(data["temperature"], float)
    assert isinstance(data["humidity"], (int, float))
    assert isinstance(data["wind_speed"], (int, float))