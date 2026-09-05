from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.schemas.user import UserCreate
from app.services import user_service


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db_session),
):
    """
    Create a new user.

    The router handles the HTTP request and delegates the
    actual user-creation logic to the service layer.
    """

    new_user = user_service.create_user(db, user)

    return {
        "user_id": new_user.user_id,
    }