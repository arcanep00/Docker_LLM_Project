import os
import uuid
from typing import List

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.db.dependency import get_db
from app.schemas.job import JobUploadResponse
from app.schemas.job_status import JobStatusResponse
from app.schemas.job_response import JobResponse
from app.schemas.transaction import TransactionResponse
from app.schemas.summary import SummaryResponse
from app.services.job_service import create_job
from app.services.job_service import get_job_by_id
from app.services.job_service import list_jobs
from app.services.transaction_service import get_transactions_by_job
from app.services.summary_service import get_summary_by_job
from app.workers.tasks import process_csv_job

router = APIRouter()


def _get_job_or_404(db: Session, job_id: int):
    job = get_job_by_id(db, job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    return job


@router.post("/upload", response_model=JobUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only csv files allowed"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    unique_name = (
        f"{uuid.uuid4()}_{file.filename}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_name
    )

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    job = create_job(
        db=db,
        filename=unique_name,
        file_path=file_path
    )
    process_csv_job.delay(job.id)

    return {
        "job_id": job.id,
        "status": job.status
    }


@router.get("", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return list_jobs(db)


@router.get(
    "/{job_id}/status",
    response_model=JobStatusResponse
)
def get_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = _get_job_or_404(db, job_id)

    return {
        "job_id": job.id,
        "status": job.status
    }


@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    return _get_job_or_404(db, job_id)


@router.get(
    "/{job_id}/transactions",
    response_model=List[TransactionResponse]
)
def get_transactions(
    job_id: int,
    anomalies_only: bool = False,
    db: Session = Depends(get_db)
):
    _get_job_or_404(db, job_id)
    return get_transactions_by_job(
        db,
        job_id,
        anomalies_only=anomalies_only
    )


@router.get(
    "/{job_id}/summary",
    response_model=SummaryResponse
)
def get_summary(
    job_id: int,
    db: Session = Depends(get_db)
):
    _get_job_or_404(db, job_id)
    summary = get_summary_by_job(db, job_id)
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail=f"Summary for job {job_id} not available yet"
        )
    return summary
