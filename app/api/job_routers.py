from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.dependency import get_db
from app.services.job_service import create_job
from app.schemas.job import JobUploadResponse
import uuid
import os

router = APIRouter()

@router.post("/upload", response_model=JobUploadResponse)

async def upload_csv(file:UploadFile = File(...),db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only csv files allowed"
        )

    unique_name = (
        f"{uuid.uuid4()}_{file.filename}"
    )

    file_path = os.path.join(
        "uploads",
        unique_name
    )

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    job = create_job(db=db, filename=unique_name,file_path=file_path)

    return {
        "job_id": job.id,
        "status": job.status
    }
