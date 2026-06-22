import pandas as pd

from app.models.Transaction import Transaction


def _clean(value):
    """Normalize a pandas/numpy cell into a DB-friendly native value.

    Converts NaN to None and numpy scalar types (e.g. numpy.float64)
    into native Python types, which psycopg2 can adapt.
    """
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except (AttributeError, ValueError):
            pass
    return value


def save_transactions(
        db,
        job_id,
        df
):
    for _, row in df.iterrows():
        txn = Transaction(
            job_id=job_id,

            txn_id=_clean(row.get("txn_id")),

            date=_clean(row.get("date")),

            merchant=_clean(row.get("merchant")),

            amount=_clean(row.get("amount")),

            currency=_clean(row.get("currency")),

            status=_clean(row.get("status")),

            category=_clean(row.get("category")),

            account_id=_clean(row.get("account_id")),

            is_anomaly=bool(row.get("is_anomaly", False)),

            anomaly_reason=_clean(
                row.get("anomaly_reason")
            ),

            llm_category=_clean(
                row.get("llm_category")
            ),

            llm_raw_response=_clean(
                row.get("llm_raw_response")
            ),

            llm_failed=bool(row.get("llm_failed", False))
        )

        db.add(txn)

    db.commit()


def get_transactions_by_job(
        db,
        job_id,
        anomalies_only=False
):
    query = db.query(
        Transaction
    ).filter(
        Transaction.job_id == job_id
    )

    if anomalies_only:
        query = query.filter(
            Transaction.is_anomaly.is_(True)
        )

    return query.order_by(
        Transaction.id
    ).all()