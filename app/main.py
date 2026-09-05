from fastapi import FastAPI

from app.routers import accounts, transactions, users


app = FastAPI(
    title="Banking API",
    description="A banking REST API built with FastAPI and PostgreSQL.",
    version="1.0.0",
)


# Register the application's routers.
#
# Each router contains endpoints for a specific part of the API.
# Including them here keeps main.py focused on application setup
# instead of business logic.
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/")
def read_root():
    """
    Basic health/info endpoint for the API.
    """

    return {
        "message": "Banking API is running."
    }