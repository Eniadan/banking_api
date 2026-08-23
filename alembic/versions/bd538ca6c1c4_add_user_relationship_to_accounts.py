"""add user relationship to accounts

Revision ID: bd538ca6c1c4
Revises: b2470238967e
Create Date: 2026-08-14 12:07:41.265404

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = 'bd538ca6c1c4'
down_revision = 'b2470238967e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """The database already has the required changes."""
    pass
    

def downgrade() -> None:
    """Nothing to undo."""
    pass