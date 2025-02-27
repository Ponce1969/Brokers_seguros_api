"""merge heads corredor sequence

Revision ID: merge_heads_corredor_sequence
Revises: 57ba78dd9ad1, fix_corredor_id_sequence
Create Date: 2025-02-27 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'merge_heads_corredor_sequence'
down_revision: Union[str, None] = ('57ba78dd9ad1', 'fix_corredor_id_sequence')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
