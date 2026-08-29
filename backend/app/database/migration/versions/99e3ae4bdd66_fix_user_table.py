"""fix:user-table

Revision ID: 99e3ae4bdd66
Revises: 85bbcf2091fd
Create Date: 2026-08-29 11:06:35.774241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99e3ae4bdd66'
down_revision: Union[str, Sequence[str], None] = '85bbcf2091fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
