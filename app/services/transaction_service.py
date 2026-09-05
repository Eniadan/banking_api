from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import AccountDB
from app.models.transaction import TransactionDB


def get_transactions(
    db: Session,
    account_id: int,
) -> list[TransactionDB]:
    """
    Retrieve all transactions belonging to an account.

    We first verify that the account exists. This allows the router
    to distinguish between an existing account with no transactions
    and an account that does not exist at all.
    """

    account = db.get(AccountDB, account_id)

    if account is None:
        raise ValueError("Account not found")

    return db.scalars(
        select(TransactionDB)
        .where(TransactionDB.account_id == account_id)
    ).all()