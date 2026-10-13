
import sqlite3
import pytest

from app import database


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Use an isolated temporary database for each test."""
    db_file = tmp_path / "test_climate.db"
    monkeypatch.setattr(database, "DB_NAME", str(db_file))
    database.init_db()
    return db_file


def test_init_db_creates_tables(test_db):
    with sqlite3.connect(test_db) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

    assert "climate_data" in tables
    assert "anomalies" in tables


def test_fetch_last_temperature_empty(test_db):
    assert database.fetch_last_temperature("Mumbai") is None


def test_save_and_fetch_last_temperature(test_db):
    database.save_climate_data("Mumbai", 30.0, 65.0, 4.0)
    database.save_climate_data("Mumbai", 32.0, 60.0, 5.0)

    assert database.fetch_last_temperature("Mumbai") == 32.0


def test_get_all_records(test_db):
    database.save_climate_data("Mumbai", 30.0, 65.0, 4.0)

    records = database.get_all_records()

    assert len(records) == 1
    assert records[0][1] == "Mumbai"
    assert records[0][2] == 30.0


def test_log_and_get_anomalies(test_db):
    database.log_anomaly("Mumbai", 36.0, 29.0)

    anomalies = database.get_anomalies()

    assert len(anomalies) == 1
    assert anomalies[0][1] == "Mumbai"
    assert anomalies[0][2] == 36.0
    assert anomalies[0][3] == 29.0
    assert anomalies[0][4] == 7.0


def test_get_last_7_records(test_db):
    for temperature in range(20, 30):
        database.save_climate_data(
            "Mumbai", float(temperature), 50.0, 3.0
        )

    records = database.get_last_7_records("Mumbai")

    assert len(records) == 7
    assert records[0][0] == 29.0
    assert records[-1][0] == 23.0


def test_records_are_filtered_by_city(test_db):
    database.save_climate_data("Mumbai", 30.0, 65.0, 4.0)
    database.save_climate_data("Hyderabad", 28.0, 55.0, 3.0)

    records = database.get_last_7_records("Hyderabad")

    assert len(records) == 1
    assert records[0][0] == 28.0


def test_get_all_records_empty(test_db):
    assert database.get_all_records() == []


def test_get_anomalies_empty(test_db):
    assert database.get_anomalies() == []
