"""agregar_corredor_id_a_usuarios

Revision ID: 02c253a26b87
Revises: 0f44d936a70b
Create Date: 2025-02-10 21:38:39.744078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02c253a26b87'
down_revision: Union[str, None] = '0f44d936a70b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar la columna corredor_id
    op.add_column('usuarios', sa.Column('corredor_id', sa.Integer(), nullable=True))
    
    # Agregar la restricción de clave foránea
    op.create_foreign_key(
        'fk_usuarios_corredor_id_corredores',
        'usuarios',
        'corredores',
        ['corredor_id'],
        ['numero']
    )


def downgrade() -> None:
    # Eliminar la restricción de clave foránea
    op.drop_constraint('fk_usuarios_corredor_id_corredores', 'usuarios', type_='foreignkey')
    
    # Eliminar la columna
    op.drop_column('usuarios', 'corredor_id')
