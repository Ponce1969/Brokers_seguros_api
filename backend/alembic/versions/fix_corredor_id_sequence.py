"""fix corredor id sequence

Revision ID: fix_corredor_id_sequence
Revises: 09c253b26c87
Create Date: 2025-02-27 01:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_corredor_id_sequence'
down_revision: Union[str, None] = '09c253b26c87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eliminar la secuencia existente si existe
    op.execute('DROP SEQUENCE IF EXISTS corredores_id_seq CASCADE')
    
    # Crear una nueva secuencia
    op.execute('CREATE SEQUENCE corredores_id_seq')
    
    # Establecer la secuencia como valor por defecto para la columna id
    op.execute('ALTER TABLE corredores ALTER COLUMN id SET DEFAULT nextval(\'corredores_id_seq\')')
    
    # Actualizar la secuencia al máximo valor actual + 1
    op.execute('''
        SELECT setval('corredores_id_seq', COALESCE((SELECT MAX(id) FROM corredores), 0) + 1, false)
    ''')


def downgrade() -> None:
    # No hacer nada en el downgrade para evitar pérdida de datos
    pass
