"""actualizar_modelo_moneda

Revision ID: c1a48cbb86c
Revises: bfaa48cbb86c
Create Date: 2025-02-11 01:25:23.744078

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1a48cbb86c"
down_revision: Union[str, None] = "bfaa48cbb86c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar la columna descripcion existente a nombre temporalmente
    op.alter_column(
        "monedas",
        "descripcion",
        new_column_name="nombre",
        existing_type=sa.String(50),
        nullable=False,
    )

    # Agregar las nuevas columnas
    op.add_column("monedas", sa.Column("simbolo", sa.String(5), nullable=True))
    op.add_column("monedas", sa.Column("descripcion", sa.String(200), nullable=True))
    op.add_column(
        "monedas", sa.Column("es_default", sa.Boolean(), server_default="false")
    )
    op.add_column(
        "monedas", sa.Column("esta_activa", sa.Boolean(), server_default="true")
    )
    op.add_column(
        "monedas",
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.add_column(
        "monedas",
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
    )

    # Hacer simbolo NOT NULL después de agregarlo
    op.execute(
        "UPDATE monedas SET simbolo = SUBSTRING(codigo FROM 1 FOR 1) WHERE simbolo IS NULL"
    )
    op.alter_column("monedas", "simbolo", existing_type=sa.String(5), nullable=False)


def downgrade() -> None:
    # Eliminar las nuevas columnas
    op.drop_column("monedas", "fecha_actualizacion")
    op.drop_column("monedas", "fecha_creacion")
    op.drop_column("monedas", "esta_activa")
    op.drop_column("monedas", "es_default")
    op.drop_column("monedas", "simbolo")
    op.drop_column("monedas", "descripcion")

    # Renombrar nombre de vuelta a descripcion
    op.alter_column(
        "monedas",
        "nombre",
        new_column_name="descripcion",
        existing_type=sa.String(50),
        nullable=False,
    )
