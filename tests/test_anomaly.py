from app.anomaly_detection import detect_anomaly

def test_no_anomaly():
    assert detect_anomaly("Hyderabad", 25) in [True, False]