from typing import Optional

from pydantic import BaseModel


class TransactionResponse(BaseModel):

    id: int

    job_id: int

    txn_id: Optional[str] = None

    date: Optional[str] = None

    merchant: Optional[str] = None

    amount: Optional[float] = None

    currency: Optional[str] = None

    status: Optional[str] = None

    category: Optional[str] = None

    account_id: Optional[str] = None

    is_anomaly: bool = False

    anomaly_reason: Optional[str] = None

    llm_category: Optional[str] = None

    llm_failed: bool = False

    class Config:
        from_attributes = True
