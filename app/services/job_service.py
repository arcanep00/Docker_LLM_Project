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

