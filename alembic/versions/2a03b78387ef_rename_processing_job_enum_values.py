"""rename processing job enum values

Revision ID: 2a03b78387ef
Revises: d305b0fe2bc2
Create Date: 2026-09-30 22:28:54.628711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a03b78387ef'
down_revision: Union[str, Sequence[str], None] = 'd305b0fe2bc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE processing_job_status "
        "RENAME VALUE 'QUEUED' TO 'queued'"
    )
    op.execute(
        "ALTER TYPE processing_job_status "
        "RENAME VALUE 'PROCESSING' TO 'processing'"
    )
    op.execute(
        "ALTER TYPE processing_job_status "
        "RENAME VALUE 'COMPLETED' TO 'completed'"
    )
    op.execute(
        "ALTER TYPE processing_job_status "
        "RENAME VALUE 'FAILED' TO 'failed'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TYPE processing_job_status "
        "RENAME VALUE 'queued' TO 'QUEUED'"
    )
    op.execute(
        "ALTER TYPE processing_job_status "
        "RENAME VALUE 'processing' TO 'PROCESSING'"
    )
    op.execute(
        "ALTER TYPE processing_job_status "
        "RENAME VALUE 'completed' TO 'COMPLETED'"
    )
    op.execute(
        "ALTER TYPE processing_job_status "
        "RENAME VALUE 'failed' TO 'FAILED'"
    )