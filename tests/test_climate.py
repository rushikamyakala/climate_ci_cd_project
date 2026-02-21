from app.climate_api import get_climate

def test_get_climate_structure():
    data = get_climate("Hyderabad")

    assert "city" in data
    assert "temperature" in data
    assert "humidity" in data
    assert "weather" in data

def test_temperature_range():
    data = get_climate("Hyderabad")

    # Temperature should be realistic
    assert -50 < data["temperature"] < 60