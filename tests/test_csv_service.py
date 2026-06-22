from app.services.csv_service import clean_csv


def _write_csv(tmp_path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "txn_id,date,merchant,amount,currency,status,category,account_id\n"
        "t1,2024-01-01,Swiggy,INR 250.50,inr,success,Food,acc1\n"
        "t2,2024-02-01,Amazon,1200.00,INR,Success,,acc1\n"
        "t2,2024-02-01,Amazon,1200.00,INR,Success,,acc1\n"  # duplicate
    )
    return str(csv_path)


def test_clean_csv_normalizes_and_dedupes(tmp_path):
    df, raw_count, clean_count = clean_csv(_write_csv(tmp_path))

    assert raw_count == 3
    assert clean_count == 2  # duplicate removed

    # amount is stripped of non-numeric chars and cast to float
    assert df["amount"].tolist() == [250.50, 1200.00]

    # status uppercased
    assert set(df["status"].tolist()) == {"SUCCESS"}

    # missing category filled
    assert "Uncategorised" in df["category"].tolist()

    # dates normalized to ISO format
    assert df["date"].iloc[0] == "2024-01-01"
    assert df["date"].notna().all()
