from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Transaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int
    account_id: int
    type: str
    amount: float
    timestamp: datetime