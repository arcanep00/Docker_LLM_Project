from app.models.job import job
from datetime import datetime


def create_job(db, filename, file_path):
    Job = job(
        filename=filename,
        file_path=file_path,
        status="pending",
        created_at=datetime.now()
    )

    db.add(Job)
    db.commit()

    db.refresh(Job)
    return Job

def update_job_status(
        db,
        job,
        status,
        error_message=None
):

    job.status = status

    if status in ("COMPLETED", "FAILED"):
        job.completed_at = datetime.now()

    if error_message is not None:
        job.error_message = error_message

    db.commit()

    db.refresh(job)

    return job

def get_job_by_id(
        db,
        job_id
):

    return db.query(
        job
    ).filter(
        job.id == job_id
    ).first()

def list_jobs(db):

    return db.query(
        job
    ).order_by(
        job.id.desc()
    ).all()

def update_row_counts(
        db,
        job,
        raw_count,
        clean_count
):

    job.row_count_raw = raw_count

    job.row_count_clean = clean_count

    db.commit()

    db.refresh(job)

    return job