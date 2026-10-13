
import pytest
from unittest.mock import Mock, patch

from app.climate_api import get_weather


@pytest.fixture
def mock_weather_response():
    return {
        "main": {
            "temp": 30.5,
            "humidity": 65,
            "pressure": 1012,
        },
        "wind": {"speed": 4.2},
        "weather": [
            {
                "main": "Clouds",
                "description": "scattered clouds",
                "icon": "03d",
            }
        ],
    }


@patch("app.climate_api.detect_anomaly", return_value=False)
@patch("app.climate_api.save_climate_data")
@patch("app.climate_api.requests.get")
def test_weather_structure(
    mock_get, mock_save, mock_anomaly, mock_weather_response, monkeypatch
):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")

    response = Mock()
    response.status_code = 200
    response.json.return_value = mock_weather_response
    mock_get.return_value = response

    data = get_weather("Hyderabad")

    assert data["temperature"] == 30.5
    assert data["humidity"] == 65
    assert data["wind_speed"] == 4.2
    assert data["weather"] == "Clouds"
    assert data["description"] == "Scattered Clouds"
    assert data["api_response_time"] >= 0

    mock_save.assert_called_once()
    mock_get.assert_called_once()
    
from unittest.mock import Mock, patch


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)

    result = get_weather("Hyderabad")

    assert result == {"error": "API key not found"}


@patch("app.climate_api.requests.get")
def test_unsuccessful_api_response(mock_get, monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")

    response = Mock()
    response.status_code = 401
    mock_get.return_value = response

    result = get_weather("Hyderabad")

    assert result == {"error": "Invalid API key or city name"}
    mock_get.assert_called_once()


@patch("app.climate_api.detect_anomaly", return_value=True)
@patch("app.climate_api.save_climate_data")
@patch("app.climate_api.requests.get")
def test_weather_response_with_anomaly(
    mock_get, mock_save, mock_anomaly, monkeypatch
):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "main": {
            "temp": 35.0,
            "humidity": 60,
            "pressure": 1010
        },
        "wind": {"speed": 3.5},
        "weather": [{
            "main": "Clear",
            "description": "clear sky",
            "icon": "01d"
        }]
    }
    mock_get.return_value = response

    result = get_weather("Hyderabad")

    assert result["temperature"] == 35.0
    assert result["anomaly"] is True
    assert result["total_execution_time"] >= 0
    mock_save.assert_called_once_with("Hyderabad", 35.0, 60, 3.5)
    mock_anomaly.assert_called_once_with("Hyderabad", 35.0)

    
from unittest.mock import patch
from app.climate_api import detect_anomaly


@patch("app.climate_api.fetch_last_temperature", return_value=None)
@patch("app.climate_api.log_anomaly")
def test_no_previous_temperature(mock_log, mock_fetch):
    result = detect_anomaly("Hyderabad", 30.0)

    assert result is False
    mock_log.assert_not_called()


@patch("app.climate_api.fetch_last_temperature", return_value=25.0)
@patch("app.climate_api.log_anomaly")
def test_anomaly_detected(mock_log, mock_fetch):
    result = detect_anomaly("Hyderabad", 35.0)

    assert result is True
    mock_log.assert_called_once_with("Hyderabad", 35.0, 25.0)


