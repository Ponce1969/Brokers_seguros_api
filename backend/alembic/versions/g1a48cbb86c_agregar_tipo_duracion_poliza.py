"""agregar_tipo_duracion_poliza

Revision ID: g1a48cbb86c
Revises: f1a48cbb86c
Create Date: 2025-02-11 02:10:23.744078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g1a48cbb86c'
down_revision: Union[str, None] = 'f1a48cbb86c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear el enum tipo_duracion
    op.execute("""
        CREATE TYPE tipo_duracion AS ENUM (
            'diaria',
            'semanal',
            'mensual',
            'trimestral',
            'semestral',
            'anual'
        )
    """)
    
    # Agregar la columna tipo_duracion con valor por defecto 'anual'
    op.add_column(
        'movimientos_vigencias',
        sa.Column(
            'tipo_duracion',
            sa.Enum('diaria', 'semanal', 'mensual', 'trimestral', 'semestral', 'anual', name='tipo_duracion'),
            server_default='anual',
            nullable=False
        )
    )


def downgrade() -> None:
    # Eliminar la columna tipo_duracion
    op.drop_column('movimientos_vigencias', 'tipo_duracion')
    
    # Eliminar el enum tipo_duracion
    op.execute('DROP TYPE tipo_duracion')
