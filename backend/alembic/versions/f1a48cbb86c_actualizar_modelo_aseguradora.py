"""actualizar_modelo_aseguradora

Revision ID: f1a48cbb86c
Revises: e1a48cbb86c
Create Date: 2025-02-11 01:40:23.744078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a48cbb86c'
down_revision: Union[str, None] = 'e1a48cbb86c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar las nuevas columnas
    op.add_column('aseguradoras', sa.Column('rut', sa.String(12), nullable=True))
    op.add_column('aseguradoras', sa.Column('esta_activa', sa.Boolean(), server_default='true'))
    op.add_column('aseguradoras', sa.Column('observaciones', sa.Text(), nullable=True))
    op.add_column('aseguradoras', sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()')))
    op.add_column('aseguradoras', sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True))
    
    # Crear índice único para rut
    op.create_unique_constraint('uq_aseguradoras_rut', 'aseguradoras', ['rut'])


def downgrade() -> None:
    # Eliminar el índice único
    op.drop_constraint('uq_aseguradoras_rut', 'aseguradoras', type_='unique')
    
    # Eliminar las nuevas columnas
    op.drop_column('aseguradoras', 'fecha_actualizacion')
    op.drop_column('aseguradoras', 'fecha_creacion')
    op.drop_column('aseguradoras', 'observaciones')
    op.drop_column('aseguradoras', 'esta_activa')
    op.drop_column('aseguradoras', 'rut')
