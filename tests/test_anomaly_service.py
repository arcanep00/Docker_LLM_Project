import pandas as pd
import pytest

from app.services.anomaly_service import detect_anomalies


def test_detect_amount_anomaly():
    df = pd.DataFrame(
        {
            "account_id": ["a", "a", "a", "a"],
            "amount": [100.0, 110.0, 90.0, 5000.0],
            "merchant": ["Swiggy", "Ola", "Zomato", "Amazon"],
            "currency": ["INR", "INR", "INR", "INR"],
        }
    )

    result = detect_anomalies(df)

    # last row is far above 3x median -> anomaly
    assert bool(result.loc[3, "is_anomaly"]) is True
    assert "3x median" in result.loc[3, "anomaly_reason"]

    # normal rows are not anomalies
    assert bool(result.loc[0, "is_anomaly"]) is False


def test_detect_currency_anomaly():
    df = pd.DataFrame(
        {
            "account_id": ["a", "a"],
            "amount": [100.0, 120.0],
            "merchant": ["Swiggy", "Amazon"],
            "currency": ["USD", "USD"],
        }
    )

    result = detect_anomalies(df)

    # domestic merchant (Swiggy) charged in USD -> anomaly
    assert bool(result.loc[0, "is_anomaly"]) is True
    assert "USD" in result.loc[0, "anomaly_reason"]

    # Amazon in USD is allowed
    assert bool(result.loc[1, "is_anomaly"]) is False


def test_detect_anomalies_missing_columns():
    df = pd.DataFrame({"amount": [1.0]})

    with pytest.raises(ValueError):
        detect_anomalies(df)
