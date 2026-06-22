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
        status
):

    job.status = status

    db.commit()

    db.refresh(job)

    return job

def get_job_by_id(
        db,
        job_id
):

    return db.query(
        Job
    ).filter(
        Job.id == job_id
    ).first()

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