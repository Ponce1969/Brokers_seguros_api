"""merge_multiple_heads

Revision ID: 8499f2969855
Revises: g1a48cbb86c, h1a48cbb86c
Create Date: 2025-02-15 23:29:27.770102

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "8499f2969855"
down_revision: Union[str, None] = ("g1a48cbb86c", "h1a48cbb86c")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
