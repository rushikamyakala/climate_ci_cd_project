# app/anomaly_detection.py

from app.database import fetch_last_temperature, log_anomaly

ANOMALY_THRESHOLD = 10  # degrees Celsius

def detect_anomaly(city, current_temp):
    previous_temp = fetch_last_temperature(city)

    if previous_temp is None:
        return False

    if abs(current_temp - previous_temp) > ANOMALY_THRESHOLD:
        log_anomaly(city, current_temp, previous_temp)
        return True

    return False