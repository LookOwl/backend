"""fix_user_columns_and_enums

Revision ID: cc0acba62ef6
Revises: da9e7c2e837f
Create Date: 2026-06-09 23:53:48.043305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'cc0acba62ef6'
down_revision: Union[str, Sequence[str], None] = 'da9e7c2e837f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('usuarios', 'nombre', type_=sa.String(length=255))
    op.alter_column('usuarios', 'email', type_=sa.String(length=255))
    op.alter_column('usuarios', 'numero_contacto', type_=sa.String(length=9))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('usuarios', 'nombre', type_=sa.String(length=30))
    op.alter_column('usuarios', 'email', type_=sa.String(length=30))
    op.alter_column('usuarios', 'numero_contacto', type_=sa.String(length=11))
