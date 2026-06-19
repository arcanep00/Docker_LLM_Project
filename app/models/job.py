from sqlalchemy import Column, String, Integer, DateTime
from app.db.base import base

class job(base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="pending"
    )

    row_count_raw = Column(
        Integer,
        default=0
    )

    row_count_clean = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime
    )

    completed_at = Column(
        DateTime
    )

    error_message = Column(
        String
    )
