"""fix processing job enum values

Revision ID: d305b0fe2bc2
Revises: 3bfbb3eb6d06
Create Date: 2026-09-30 22:23:21.551554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd305b0fe2bc2'
down_revision: Union[str, Sequence[str], None] = '3bfbb3eb6d06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
