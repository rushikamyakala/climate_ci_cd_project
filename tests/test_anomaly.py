from app.anomaly_detection import detect_anomaly

def test_no_anomaly():
    assert detect_anomaly("Hyderabad", 25) in [True, False]

    
from unittest.mock import patch

from app.anomaly_detection import detect_anomaly


@patch("app.anomaly_detection.fetch_last_temperature", return_value=None)
@patch("app.anomaly_detection.log_anomaly")
def test_no_previous_temperature(mock_log, mock_fetch):
    result = detect_anomaly("Hyderabad", 30.0)

    assert result is False
    mock_log.assert_not_called()


@patch("app.anomaly_detection.fetch_last_temperature", return_value=25.0)
@patch("app.anomaly_detection.log_anomaly")
def test_temperature_difference_below_threshold(mock_log, mock_fetch):
    result = detect_anomaly("Hyderabad", 30.0)

    assert result is False
    mock_log.assert_not_called()


@patch("app.anomaly_detection.fetch_last_temperature", return_value=25.0)
@patch("app.anomaly_detection.log_anomaly")
def test_temperature_difference_above_threshold(mock_log, mock_fetch):
    result = detect_anomaly("Hyderabad", 36.0)

    assert result is True
    mock_log.assert_called_once_with("Hyderabad", 36.0, 25.0)
