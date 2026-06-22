from app.services.llm_service import (
    safe_gemini_call
)
from app.models.job_summary import (
    JobSummary
)

def calculate_total_inr(df):
    return (
        df[
            df["currency"] == "INR"
            ]["amount"]
        .sum()
    )

def calculate_total_usd(df):
    return (
        df[
            df["currency"] == "USD"
            ]["amount"]
        .sum()
    )

def get_top_merchants(df):
    merchant_totals = (
        df.groupby("merchant")
        ["amount"]
        .sum()
    )
    merchant_totals = (
        merchant_totals
        .sort_values(
            ascending=False
        )
    )
    top_merchants = (
        merchant_totals
        .head(3)
        .index
        .tolist()
    )
    return top_merchants

def get_anomaly_count(df):
    return len(
        df[
            df["is_anomaly"] == True
            ]
    )

def calculate_risk_level(
    anomaly_count
):
    if anomaly_count == 0:
        return "low"

    if anomaly_count <= 5:
        return "medium"

    return "high"

def build_summary_prompt(
    total_inr,
    total_usd,
    top_merchants,
    anomaly_count,
    risk_level
):
    return f"""
    Generate a concise financial summary.

    Data:

    Total INR Spend:
    {total_inr}

    Total USD Spend:
    {total_usd}

    Top Merchants:
    {top_merchants}

    Anomaly Count:
    {anomaly_count}

    Risk Level:
    {risk_level}

    Return 3-4 sentences.
    """

def generate_narrative(
    total_inr,
    total_usd,
    top_merchants,
    anomaly_count,
    risk_level
):

    prompt = build_summary_prompt(
        total_inr,
        total_usd,
        top_merchants,
        anomaly_count,
        risk_level
    )

    narrative = safe_gemini_call(
        prompt
    )

    return narrative

def generate_summary(df):
    total_inr = (
        calculate_total_inr(df)
    )
    total_usd = (
        calculate_total_usd(df)
    )

    top_merchants = (
        get_top_merchants(df)
    )
    anomaly_count = (
        get_anomaly_count(df)
    )

    risk_level = (
        calculate_risk_level(
            anomaly_count
        )
    )

    narrative = (
        generate_narrative(
            total_inr,
            total_usd,
            top_merchants,
            anomaly_count,
            risk_level
        )
    )

    return {
        "total_spend_inr": total_inr,
        "total_spend_usd": total_usd,
        "top_merchants": top_merchants,
        "anomaly_count": anomaly_count,
        "narrative": narrative,
        "risk_level": risk_level
    }

def save_summary(
    db,
    job_id,
    summary
):
    job_summary = JobSummary(
        job_id=job_id,

        total_spend_inr=summary[
            "total_spend_inr"
        ],

        total_spend_usd=summary[
            "total_spend_usd"
        ],

        top_merchants=str(
            summary[
                "top_merchants"
            ]
        ),

        anomaly_count=summary[
            "anomaly_count"
        ],

        narrative=summary[
            "narrative"
        ],

        risk_level=summary[
            "risk_level"
        ]
    )

    db.add(job_summary)

    db.commit()





















