from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.schemas.transaction import Transaction
from app.services import transaction_service


router = APIRouter(
    prefix="/accounts",
    tags=["Transactions"],
)


@router.get(
    "/{account_id}/transactions",
    response_model=list[Transaction],
)
def get_transactions(
    account_id: int,
    db: Session = Depends(get_db_session),
):
    """
    Return all transactions belonging to an account.

    The router handles the HTTP response while the service
    handles the database/business logic.
    """

    try:
        return transaction_service.get_transactions(
            db,
            account_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )