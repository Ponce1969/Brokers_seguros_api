"""restaurar_relaciones_usuario

Revision ID: 57ba78dd9ad1
Revises: 8499f2969855
Create Date: 2025-02-15 23:30:29.937367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57ba78dd9ad1'
down_revision: Union[str, None] = '8499f2969855'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('tipos_documento_descripcion_key', 'tipos_documento', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('tipos_documento_descripcion_key', 'tipos_documento', ['nombre'])
    # ### end Alembic commands ###
