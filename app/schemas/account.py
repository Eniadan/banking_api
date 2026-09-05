from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    user_id: int


class Account(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    user_id: int
    balance: float