import pandas as pd

from app.services import llm_service
from app.services.llm_service import (
    apply_categories,
    classify_merchants,
    enrich_categories,
)


def test_classify_merchants_parses_json(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "safe_gemini_call",
        lambda prompt: '```json\n{"Swiggy": "Food", "Uber": "Transport"}\n```',
    )

    classifications, raw, failed = classify_merchants(["Swiggy", "Uber"])

    assert failed is False
    assert classifications == {"Swiggy": "Food", "Uber": "Transport"}


def test_classify_merchants_invalid_json(monkeypatch):
    monkeypatch.setattr(
        llm_service,
        "safe_gemini_call",
        lambda prompt: "not json at all",
    )

    classifications, raw, failed = classify_merchants(["Swiggy"])

    assert failed is True
    assert classifications == {}


def test_apply_categories_overwrites_uncategorised():
    df = pd.DataFrame(
        {
            "merchant": ["Swiggy", "Uber"],
            "category": ["Uncategorised", "Uncategorised"],
        }
    )

    result = apply_categories(df, {"Swiggy": "Food"})

    assert result.loc[0, "category"] == "Food"
    assert result.loc[0, "llm_category"] == "Food"


def test_enrich_categories_no_uncategorised_is_noop(monkeypatch):
    def _boom(*args, **kwargs):
        raise AssertionError("LLM should not be called")

    monkeypatch.setattr(llm_service, "safe_gemini_call", _boom)

    df = pd.DataFrame(
        {
            "merchant": ["Swiggy"],
            "category": ["Food"],
        }
    )

    result = enrich_categories(df)
    assert result.loc[0, "category"] == "Food"
