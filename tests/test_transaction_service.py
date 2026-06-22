import pandas as pd

from app.services.job_service import create_job
from app.services.transaction_service import (
    get_transactions_by_job,
    save_transactions,
)


def test_save_and_fetch_transactions(db_session):
    job = create_job(
        db_session,
        filename="f.csv",
        file_path="uploads/f.csv",
    )

    df = pd.DataFrame(
        {
            "txn_id": ["t1", "t2"],
            "date": ["2024-01-01", "2024-01-02"],
            "merchant": ["Swiggy", "Amazon"],
            "amount": [100.0, 5000.0],
            "currency": ["INR", "INR"],
            "status": ["SUCCESS", "SUCCESS"],
            "category": ["Food", "Shopping"],
            "account_id": ["a1", "a1"],
            "is_anomaly": [False, True],
            "anomaly_reason": [None, "Amount exceeds 3x median"],
        }
    )

    save_transactions(db_session, job.id, df)

    all_txns = get_transactions_by_job(db_session, job.id)
    assert len(all_txns) == 2

    anomalies = get_transactions_by_job(
        db_session, job.id, anomalies_only=True
    )
    assert len(anomalies) == 1
    assert anomalies[0].txn_id == "t2"
    assert anomalies[0].anomaly_reason == "Amount exceeds 3x median"
    # NaN-safe: None stays None
    assert all_txns[0].anomaly_reason is None
