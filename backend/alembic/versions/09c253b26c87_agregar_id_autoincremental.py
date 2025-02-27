"""Agregar id autoincremental y cambiar numero a campo único

Revision ID: 09c253b26c87
Revises: 2a95db305778
Create Date: 2025-02-25 20:45:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09c253b26c87'
down_revision = '2a95db305778'  # Asegúrate de que este sea el ID correcto de la última revisión
branch_labels = None
depends_on = None


def upgrade():
    # Paso 1: Agregar columna id con autoincrement, inicialmente permitiendo nulos
    op.add_column('corredores', sa.Column('id', sa.Integer(), autoincrement=True, nullable=True))
    
    # Paso 2: Llenar la columna id con valores secuenciales basados en la columna numero
    op.execute("UPDATE corredores SET id = numero")
    
    # Paso 3: Hacer la columna id NOT NULL después de que tenga valores
    op.alter_column('corredores', 'id', nullable=False)
    
    # Paso 4: Crear índice en la nueva columna id
    op.create_index(op.f('ix_corredores_id'), 'corredores', ['id'], unique=True)
    
    # Paso 5: Modificar las tablas dependientes para usar id en lugar de numero

    # Crear columna corredor_id en tabla usuarios
    op.add_column('usuarios', sa.Column('corredor_id', sa.Integer(), nullable=True))
    # Copiar valores del número de corredor al nuevo campo id
    op.execute("UPDATE usuarios SET corredor_id = (SELECT id FROM corredores WHERE corredores.numero = usuarios.corredor_numero)")
    # Eliminar clave foránea antigua
    op.drop_constraint('usuarios_corredor_numero_fkey', 'usuarios', type_='foreignkey')
    # Crear nueva clave foránea
    op.create_foreign_key('usuarios_corredor_id_fkey', 'usuarios', 'corredores', ['corredor_id'], ['id'])
    
    # Crear columna corredor_id en tabla clientes_corredores
    op.add_column('clientes_corredores', sa.Column('corredor_id', sa.Integer(), nullable=True))
    # Copiar valores
    op.execute("UPDATE clientes_corredores SET corredor_id = (SELECT id FROM corredores WHERE corredores.numero = clientes_corredores.corredor_numero)")
    # Eliminar clave foránea antigua
    op.drop_constraint('clientes_corredores_corredor_numero_fkey', 'clientes_corredores', type_='foreignkey')
    # Crear nueva clave foránea
    op.create_foreign_key('clientes_corredores_corredor_id_fkey', 'clientes_corredores', 'corredores', ['corredor_id'], ['id'])
    
    # Modificar movimientos_vigencias (si usa corredor_id o corredor_numero)
    # Asumiendo que usa corredor_id pero está referenciando a numero
    op.drop_constraint('movimientos_vigencias_corredor_id_fkey', 'movimientos_vigencias', type_='foreignkey')
    op.create_foreign_key('movimientos_vigencias_corredor_id_fkey', 'movimientos_vigencias', 'corredores', ['corredor_id'], ['id'])
    
    # Paso 6: Modificar la clave primaria de la tabla corredores
    op.execute("ALTER TABLE corredores DROP CONSTRAINT corredores_pkey")
    op.execute("ALTER TABLE corredores ADD PRIMARY KEY (id)")
    
    # Paso 7: Asegurarse de que numero sea UNIQUE pero no clave primaria
    op.create_unique_constraint('uq_corredores_numero', 'corredores', ['numero'])


def downgrade():
    # Paso 1: Modificar las tablas dependientes para usar numero en lugar de id

    # Revertir cambios en tabla usuarios
    op.drop_constraint('usuarios_corredor_id_fkey', 'usuarios', type_='foreignkey')
    op.create_foreign_key('usuarios_corredor_numero_fkey', 'usuarios', 'corredores', ['corredor_numero'], ['numero'])
    op.drop_column('usuarios', 'corredor_id')
    
    # Revertir cambios en tabla clientes_corredores
    op.drop_constraint('clientes_corredores_corredor_id_fkey', 'clientes_corredores', type_='foreignkey')
    op.create_foreign_key('clientes_corredores_corredor_numero_fkey', 'clientes_corredores', 'corredores', ['corredor_numero'], ['numero'])
    op.drop_column('clientes_corredores', 'corredor_id')
    
    # Revertir cambios en movimientos_vigencias
    op.drop_constraint('movimientos_vigencias_corredor_id_fkey', 'movimientos_vigencias', type_='foreignkey')
    op.create_foreign_key('movimientos_vigencias_corredor_id_fkey', 'movimientos_vigencias', 'corredores', ['corredor_id'], ['numero'])
    
    # Paso 2: Revertir cambios en la tabla corredores
    op.drop_constraint('uq_corredores_numero', 'corredores', type_='unique')
    op.execute("ALTER TABLE corredores DROP CONSTRAINT corredores_pkey")
    op.execute("ALTER TABLE corredores ADD PRIMARY KEY (numero)")
    op.drop_index(op.f('ix_corredores_id'), table_name='corredores')
    op.drop_column('corredores', 'id')
