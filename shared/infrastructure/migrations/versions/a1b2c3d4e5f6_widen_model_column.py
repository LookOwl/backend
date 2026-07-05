"""widen model column in libro_embeddings

Revision ID: a1b2c3d4e5f6
Revises: 94617cf9ee03
Create Date: 2026-07-01 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '94617cf9ee03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'libro_embeddings',
        'model',
        existing_type=sa.String(50),
        type_=sa.String(255),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'libro_embeddings',
        'model',
        existing_type=sa.String(255),
        type_=sa.String(50),
        existing_nullable=False,
    )
