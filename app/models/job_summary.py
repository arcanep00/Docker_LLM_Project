from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.base import base

class JobSummary(base):

    __tablename__ = "job_summaries"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id")
    )

    total_spend_inr = Column(
        Float
    )

    total_spend_usd = Column(
        Float
    )

    top_merchants = Column(
        String
    )

    anamoly_count = Column(
        Integer
    )

    narrative = Column(
        String
    )

    risk_level = Column(
        String
    )