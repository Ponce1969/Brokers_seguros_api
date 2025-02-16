"""cambiar rut a identificador fiscal en aseguradoras

Revision ID: h1a48cbb86c
Revises: f1a48cbb86c
Create Date: 2024-02-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h1a48cbb86c'
down_revision: Union[str, None] = 'f1a48cbb86c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar la columna y agregar el comentario
    op.alter_column('aseguradoras', 'rut',
                    new_column_name='identificador_fiscal',
                    existing_type=sa.String(12),
                    existing_nullable=True,
                    comment="Identificador fiscal de la aseguradora (RUT, CUIT, NIF, etc.)")


def downgrade() -> None:
    # Revertir los cambios
    op.alter_column('aseguradoras', 'identificador_fiscal',
                    new_column_name='rut',
                    existing_type=sa.String(12),
                    existing_nullable=True)
