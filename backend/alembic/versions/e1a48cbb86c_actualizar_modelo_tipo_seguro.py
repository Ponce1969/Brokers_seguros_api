"""actualizar_modelo_tipo_seguro

Revision ID: e1a48cbb86c
Revises: d1a48cbb86c
Create Date: 2025-02-11 01:35:23.744078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a48cbb86c'
down_revision: Union[str, None] = 'd1a48cbb86c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar las nuevas columnas
    op.add_column('tipos_de_seguros', sa.Column('codigo', sa.String(10), nullable=True))
    op.add_column('tipos_de_seguros', sa.Column('nombre', sa.String(100), nullable=True))
    op.add_column('tipos_de_seguros', sa.Column('descripcion', sa.Text(), nullable=True))
    op.add_column('tipos_de_seguros', sa.Column('es_default', sa.Boolean(), server_default='false'))
    op.add_column('tipos_de_seguros', sa.Column('esta_activo', sa.Boolean(), server_default='true'))
    op.add_column('tipos_de_seguros', sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()')))
    op.add_column('tipos_de_seguros', sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True))
    
    # Actualizar registros existentes
    op.execute("""
        UPDATE tipos_de_seguros 
        SET codigo = 'SEG-' || id::text,
            nombre = categoria || ' - ' || substring(cobertura from 1 for 50)
        WHERE codigo IS NULL
    """)
    
    # Hacer las columnas NOT NULL después de la actualización
    op.alter_column('tipos_de_seguros', 'codigo',
                   existing_type=sa.String(10),
                   nullable=False)
    op.alter_column('tipos_de_seguros', 'nombre',
                   existing_type=sa.String(100),
                   nullable=False)
    
    # Crear índice único para codigo
    op.create_unique_constraint('uq_tipos_de_seguros_codigo', 'tipos_de_seguros', ['codigo'])


def downgrade() -> None:
    # Eliminar el índice único
    op.drop_constraint('uq_tipos_de_seguros_codigo', 'tipos_de_seguros', type_='unique')
    
    # Eliminar las nuevas columnas
    op.drop_column('tipos_de_seguros', 'fecha_actualizacion')
    op.drop_column('tipos_de_seguros', 'fecha_creacion')
    op.drop_column('tipos_de_seguros', 'esta_activo')
    op.drop_column('tipos_de_seguros', 'es_default')
    op.drop_column('tipos_de_seguros', 'descripcion')
    op.drop_column('tipos_de_seguros', 'nombre')
    op.drop_column('tipos_de_seguros', 'codigo')
