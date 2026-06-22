import io


def test_root_and_health(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}


def test_list_jobs_empty(client):
    resp = client.get("/jobs")
    assert resp.status_code == 200
    assert resp.json() == []


def test_upload_rejects_non_csv(client):
    resp = client.post(
        "/jobs/upload",
        files={"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400


def test_upload_and_status_flow(client):
    csv_bytes = (
        b"txn_id,date,merchant,amount,currency,status,category,account_id\n"
        b"t1,2024-01-01,Swiggy,100,INR,SUCCESS,Food,a1\n"
    )

    resp = client.post(
        "/jobs/upload",
        files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]
    assert resp.json()["status"] == "pending"

    status = client.get(f"/jobs/{job_id}/status")
    assert status.status_code == 200
    assert status.json()["job_id"] == job_id

    # job appears in listing
    listing = client.get("/jobs")
    assert any(j["id"] == job_id for j in listing.json())

    # transactions empty until worker runs
    txns = client.get(f"/jobs/{job_id}/transactions")
    assert txns.status_code == 200
    assert txns.json() == []

    # summary not available yet
    summary = client.get(f"/jobs/{job_id}/summary")
    assert summary.status_code == 404


def test_unknown_job_returns_404(client):
    assert client.get("/jobs/999999/status").status_code == 404
    assert client.get("/jobs/999999/transactions").status_code == 404
