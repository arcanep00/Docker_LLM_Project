from pydantic import BaseModel

class ResultResponse(BaseModel):

    transactions: list

    anomalies: list

    category_breakdown: dict

    summary: dict