from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.account import AccountDB
from app.models.transaction import TransactionDB
from app.schemas.account import AccountCreate
from app.schemas.transaction_request import DepositRequest, WithdrawRequest


def create_account(db: Session, account: AccountCreate) -> AccountDB:
    """
    Create a new bank account for an existing user.
    """

    new_account = AccountDB(
        user_id=account.user_id,
        balance=0.0,
    )

    try:
        db.add(new_account)
        db.commit()
        db.refresh(new_account)

        return new_account

    except SQLAlchemyError:
        db.rollback()
        raise


def get_account(db: Session, account_id: int) -> AccountDB | None:
    """
    Retrieve one account by its ID.

    Returns None when the account does not exist.
    """

    return db.get(AccountDB, account_id)


def list_accounts(db: Session) -> list[AccountDB]:
    """
    Retrieve all bank accounts.
    """

    return db.scalars(
        select(AccountDB)
    ).all()


def deposit(
    db: Session,
    account_id: int,
    deposit_request: DepositRequest,
) -> AccountDB:
    """
    Deposit money into an account and record the transaction.

    The balance update and transaction record are committed
    together so the database does not end up with only one
    of the two operations.
    """

    account = db.get(AccountDB, account_id)

    if account is None:
        raise ValueError("Account not found")

    account.balance += deposit_request.amount

    transaction = TransactionDB(
        account_id=account.account_id,
        type="deposit",
        amount=deposit_request.amount,
    )

    db.add(transaction)

    try:
        db.commit()
        db.refresh(account)

        return account

    except SQLAlchemyError:
        db.rollback()
        raise


def withdraw(
    db: Session,
    account_id: int,
    withdraw_request: WithdrawRequest,
) -> AccountDB:
    """
    Withdraw money while preventing the balance from becoming negative.

    The balance check happens inside the SQL UPDATE itself. This is
    important because two requests could attempt to withdraw money
    from the same account at nearly the same time.
    """

    amount = withdraw_request.amount

    account = db.get(AccountDB, account_id)

    if account is None:
        raise ValueError("Account not found")

    # The condition is evaluated by PostgreSQL as part of the UPDATE.
    # Therefore the database will only subtract the money if enough
    # money is currently available.
    result = db.execute(
        update(AccountDB)
        .where(
            AccountDB.account_id == account_id,
            AccountDB.balance >= amount,
        )
        .values(
            balance=AccountDB.balance - amount,
        )
    )

    # No row updated means the account either did not have enough
    # money or the account could not be updated.
    if result.rowcount == 0:
        db.rollback()
        raise ValueError("Insufficient funds")

    transaction = TransactionDB(
        account_id=account_id,
        type="withdraw",
        amount=amount,
    )

    db.add(transaction)

    try:
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(account)

    return account