"""fix corredor sequences

Revision ID: fix_corredor_sequences
Revises: merge_heads_corredor_sequence
Create Date: 2025-02-27 02:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_corredor_sequences'
down_revision: Union[str, None] = 'merge_heads_corredor_sequence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eliminar la secuencia del numero ya que debe ser asignado por el admin
    op.execute('ALTER TABLE corredores ALTER COLUMN numero DROP DEFAULT')
    op.execute('DROP SEQUENCE IF EXISTS corredores_numero_seq')
    
    # Asegurar que la secuencia del id está correctamente configurada
    op.execute('''
        SELECT setval('corredores_id_seq', COALESCE((SELECT MAX(id) FROM corredores), 0) + 1, false)
    ''')


def downgrade() -> None:
    # No hacer nada en el downgrade para evitar pérdida de datos
    pass
