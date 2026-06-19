from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from app.db.base import base

class Transaction(base):
    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id = Column(Integer,
                    ForeignKey("jobs.id"))

    txn_id = Column(String)

    date = Column(String)

    merchant = Column(String)

    amount = Column(Float)

    currency = Column(String)

    status = Column(String)

    category = Column(String)

    account_id = Column(String)

    is_anamoly = Column(
        Boolean,
        default=False
    )

    anamoly_reason = Column(
        String
    )

    llm_category = Column(
        String
    )

    llm_raw_response = Column(
        String
    )

    llm_failed = Column(
        Boolean,
        default=False
    )

