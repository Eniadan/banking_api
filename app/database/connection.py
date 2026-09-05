import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


# Load variables from the .env file.
load_dotenv()

# Get the database connection URL from the environment.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment.")


# Create the SQLAlchemy engine.
# The engine manages communication between our application
# and the PostgreSQL database.
engine = create_engine(DATABASE_URL)


def get_db_session():
    """
    Provide a database session to FastAPI endpoints.

    The session is automatically closed after the request finishes.
    """
    db = Session(engine)

    try:
        yield db
    finally:
        db.close()