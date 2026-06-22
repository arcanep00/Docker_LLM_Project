from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobResponse(BaseModel):

    id: int

    filename: str

    status: str

    row_count_raw: Optional[int] = None

    row_count_clean: Optional[int] = None

    created_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):

    job_id: int

    status: str
