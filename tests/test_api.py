import pytest
from app.climate_api import get_weather

def test_weather_structure():
    data = get_weather("Hyderabad")
    assert "temperature" in data
    assert "humidity" in data
    assert "wind_speed" in data