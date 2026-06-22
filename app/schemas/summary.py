from typing import Optional

from pydantic import BaseModel


class SummaryResponse(BaseModel):

    id: int

    job_id: int

    total_spend_inr: Optional[float] = None

    total_spend_usd: Optional[float] = None

    top_merchants: Optional[str] = None

    anomaly_count: Optional[int] = None

    narrative: Optional[str] = None

    risk_level: Optional[str] = None

    class Config:
        from_attributes = True
