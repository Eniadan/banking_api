from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.schemas.account import Account, AccountCreate
from app.schemas.transaction_request import DepositRequest, WithdrawRequest
from app.services import account_service


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)


@router.get("/", response_model=list[Account])
def list_accounts(
    db: Session = Depends(get_db_session),
):
    """Return all bank accounts."""

    return account_service.list_accounts(db)


@router.get("/{account_id}", response_model=Account)
def get_account(
    account_id: int,
    db: Session = Depends(get_db_session),
):
    """Return one account by its ID."""

    account = account_service.get_account(db, account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return account


@router.post("/", response_model=Account)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db_session),
):
    """Create a new bank account."""

    try:
        return account_service.create_account(db, account)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to create account",
        )


@router.post("/{account_id}/deposit", response_model=Account)
def deposit(
    account_id: int,
    deposit_request: DepositRequest,
    db: Session = Depends(get_db_session),
):
    """Deposit money into an account."""

    try:
        return account_service.deposit(
            db,
            account_id,
            deposit_request,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to process deposit",
        )


@router.post("/{account_id}/withdraw", response_model=Account)
def withdraw(
    account_id: int,
    withdraw_request: WithdrawRequest,
    db: Session = Depends(get_db_session),
):
    """Withdraw money from an account."""

    try:
        return account_service.withdraw(
            db,
            account_id,
            withdraw_request,
        )

    except ValueError as error:
        # The service uses ValueError for business failures such as
        # a missing account or insufficient funds. The router converts
        # those into appropriate HTTP responses.
        if str(error) == "Account not found":
            status_code = 404
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=str(error),
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to process withdrawal",
        )