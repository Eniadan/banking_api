from pydantic import BaseModel, Field


class DepositRequest(BaseModel):
    amount: float = Field(
        gt=0,
        description="Amount to deposit, must be greater than zero",
    )


class WithdrawRequest(BaseModel):
    amount: float = Field(
        gt=0,
        description="Amount to withdraw, must be greater than zero",
    )