from typing import List
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel,Field,ConfigDict
from sqlalchemy import (create_engine, Integer, String, Float, DateTime, ForeignKey, select,update)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.exc import SQLAlchemyError



DATABASE_URL = "postgresql+psycopg://postgres:patrician4268@localhost:5432/banking"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_db_session():
    db=Session(engine)
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass

class UserDB(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    #email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AccountDB(Base):
    __tablename__ = "accounts"
    account_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0)

class TransactionDB(Base):
    __tablename__ = "transactions"
    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.account_id"),nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

class Account(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    user_id: int
    balance: float


class AccountCreate(BaseModel):
    user_id: int

class User(BaseModel):
    name:str=Field(min_length=1)

class DepositRequest(BaseModel):
    amount: float=Field(gt=0, description="Amount to deposit, must be greater than zero")

class WithdrawRequest(BaseModel):
    amount: float=Field(gt=0, description="Amount to withdraw, must be greater than zero")

class Transaction (BaseModel):
    model_config = ConfigDict(from_attributes=True)
    transaction_id: int
    account_id: int
    type: str
    amount: float
    timestamp: datetime

app = FastAPI()

@app.post("/users/", response_model=dict)
def create_user(user: User, db: Session = Depends(get_db_session)):
    new_user = UserDB(name=user.name)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"user_id": new_user.user_id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="FAILED TO CREATE USER")

@app.get("/")
def read_root():
    return {"message": "Use /accounts/{account_id} to fetch an account or POST /accounts/ to create one."}


@app.get("/accounts/", response_model=List[Account])
def list_accounts(db: Session = Depends(get_db_session)):
    accounts=db.scalars(select(AccountDB)).all()
    return accounts
    


@app.get("/accounts/{account_id}", response_model=Account)
def read_account(account_id: int,db: Session = Depends(get_db_session)):
    account = db.get(AccountDB, account_id)
    if account is None: 
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.post("/accounts/", response_model=Account)
def create_account(account: AccountCreate,db: Session = Depends(get_db_session)):
    new_account = AccountDB(
        user_id=account.user_id,
        balance=0.0
    )
    try:
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        return new_account
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="FAILED TO CREATE ACCOUNT")

@app.post("/accounts/{account_id}/deposit", response_model=Account)
def deposit(account_id: int, deposit: DepositRequest,db: Session = Depends(get_db_session)):
    account = db.get(AccountDB, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if deposit.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be greater than zero")
    account.balance += deposit.amount
    transaction=TransactionDB(
        account_id=account.account_id,
        type="deposit",
        amount=deposit.amount,
    )
    db.add(transaction)
    db.commit()
    db.refresh(account)
    return account



@app.post("/accounts/{account_id}/withdraw", response_model=Account)
def withdraw(account_id: int, withdraw_request: WithdrawRequest,db: Session = Depends(get_db_session)):
    amount=withdraw_request.amount
    account = db.get(AccountDB, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    result = db.execute(update(AccountDB).where(AccountDB.account_id == account_id, AccountDB.balance >= amount).values(balance=AccountDB.balance - amount))
    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    transaction=TransactionDB(account_id=account.account_id,type="withdraw",amount=amount)
    db.add(transaction)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="FAILED TO WITHDRAW")
    db.refresh(account)
    return account
@app.get("/accounts/{account_id}/transactions", response_model=List[Transaction])
def get_transactions(account_id: int,db: Session = Depends(get_db_session)):
    account = db.get(AccountDB, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db.scalars(select(TransactionDB).where(TransactionDB.account_id == account_id)).all()

