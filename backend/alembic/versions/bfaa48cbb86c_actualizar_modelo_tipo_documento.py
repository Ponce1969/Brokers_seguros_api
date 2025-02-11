"""actualizar_modelo_tipo_documento

Revision ID: bfaa48cbb86c
Revises: 2a95db305778
Create Date: 2025-02-11 01:19:23.744078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfaa48cbb86c'
down_revision: Union[str, None] = '2a95db305778'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar la columna descripcion existente a nombre temporalmente
    op.alter_column('tipos_documento', 'descripcion',
                   new_column_name='nombre',
                   existing_type=sa.String(50),
                   nullable=False)
    
    # Agregar las nuevas columnas
    op.add_column('tipos_documento', sa.Column('codigo', sa.String(10), nullable=True))
    op.add_column('tipos_documento', sa.Column('descripcion', sa.String(200), nullable=True))
    op.add_column('tipos_documento', sa.Column('es_default', sa.Boolean(), server_default='false'))
    op.add_column('tipos_documento', sa.Column('esta_activo', sa.Boolean(), server_default='true'))
    
    # Crear un índice único para codigo
    op.create_unique_constraint('uq_tipos_documento_codigo', 'tipos_documento', ['codigo'])
    
    # Actualizar los registros existentes con valores por defecto para codigo
    op.execute("UPDATE tipos_documento SET codigo = SUBSTRING(nombre FROM 1 FOR 10) WHERE codigo IS NULL")
    
    # Hacer codigo NOT NULL después de la actualización
    op.alter_column('tipos_documento', 'codigo',
                   existing_type=sa.String(10),
                   nullable=False)


def downgrade() -> None:
    # Eliminar las nuevas columnas
    op.drop_constraint('uq_tipos_documento_codigo', 'tipos_documento', type_='unique')
    op.drop_column('tipos_documento', 'esta_activo')
    op.drop_column('tipos_documento', 'es_default')
    op.drop_column('tipos_documento', 'codigo')
    
    # Renombrar nombre de vuelta a descripcion
    op.alter_column('tipos_documento', 'nombre',
                   new_column_name='descripcion',
                   existing_type=sa.String(50),
                   nullable=False)
