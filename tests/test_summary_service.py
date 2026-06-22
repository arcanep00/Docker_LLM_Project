import pandas as pd

from app.services import summary_service
from app.services.summary_service import (
    calculate_risk_level,
    calculate_total_inr,
    calculate_total_usd,
    generate_summary,
    get_anomaly_count,
    get_top_merchants,
)


def _df():
    return pd.DataFrame(
        {
            "merchant": ["Swiggy", "Amazon", "Swiggy", "Uber"],
            "amount": [100.0, 500.0, 50.0, 80.0],
            "currency": ["INR", "INR", "USD", "USD"],
            "is_anomaly": [False, True, False, True],
        }
    )


def test_totals_and_merchants():
    df = _df()
    assert calculate_total_inr(df) == 600.0
    assert calculate_total_usd(df) == 130.0
    assert get_anomaly_count(df) == 2
    assert "Amazon" in get_top_merchants(df)


def test_risk_levels():
    assert calculate_risk_level(0) == "low"
    assert calculate_risk_level(3) == "medium"
    assert calculate_risk_level(10) == "high"


def test_generate_summary_uses_llm(monkeypatch):
    monkeypatch.setattr(
        summary_service,
        "safe_gemini_call",
        lambda prompt: "Mock narrative.",
    )

    result = generate_summary(_df())

    assert result["total_spend_inr"] == 600.0
    assert result["anomaly_count"] == 2
    assert result["risk_level"] == "medium"
    assert result["narrative"] == "Mock narrative."
