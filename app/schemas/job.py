from pydantic import BaseModel

class JobUploadResponse(BaseModel):
    job_id: int
    status: str