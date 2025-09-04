"""Secuencia en ids usuarios (Oracle-safe)
Revision ID: 25555ea04d22
Revises: f575331f1950
Create Date: 2025-09-02 15:13:55.085741
"""
from alembic import op
import sqlalchemy as sa

revision = "25555ea04d22"
down_revision = "f575331f1950"
branch_labels = None
depends_on = None

# ---------- Helpers ----------
def column_exists(bind, table, column):
    insp = sa.inspect(bind)
    return any(c["name"].upper() == column.upper()
               for c in insp.get_columns(table_name=table))

def drop_unique_on_column_if_any(bind, table, column):
    sql = sa.text("""
        SELECT uc.constraint_name
        FROM user_constraints uc
        JOIN user_cons_columns ucc
          ON uc.constraint_name = ucc.constraint_name
        WHERE uc.table_name = :t
          AND uc.constraint_type = 'U'
          AND ucc.column_name = :c
    """)
    rows = bind.execute(sql, {"t": table.upper(), "c": column.upper()}).fetchall()
    for (name,) in rows:
        bind.exec_driver_sql(f'ALTER TABLE {table} DROP CONSTRAINT "{name}"')

def drop_fk_on_column_if_any(bind, table, column):
    sql = sa.text("""
        SELECT uc.constraint_name
        FROM user_constraints uc
        JOIN user_cons_columns ucc
          ON uc.constraint_name = ucc.constraint_name
        WHERE uc.table_name = :t
          AND uc.constraint_type = 'R'
          AND ucc.column_name = :c
    """)
    rows = bind.execute(sql, {"t": table.upper(), "c": column.upper()}).fetchall()
    for (name,) in rows:
        bind.exec_driver_sql(f'ALTER TABLE {table} DROP CONSTRAINT "{name}"')

def sequence_exists(bind, seq_name):
    row = bind.execute(
        sa.text("SELECT COUNT(1) FROM user_sequences WHERE sequence_name = :s"),
        {"s": seq_name.upper()},
    ).fetchone()
    return bool(row and row[0] == 1)

def create_sequence_if_missing(bind, seq_name, start_with=1, increment_by=1):
    if not sequence_exists(bind, seq_name):
        bind.exec_driver_sql(
            f'CREATE SEQUENCE {seq_name} START WITH {start_with} INCREMENT BY {increment_by}'
        )

def upgrade():
    bind = op.get_bind()

    # (Opcional) asegura la secuencia del ID si tu modelo usa Sequence('usuario_id_seq')
    create_sequence_if_missing(bind, "USUARIO_ID_SEQ")

    # Primero elimina constraints, NO índices SYS_C...
    if column_exists(bind, "USUARIOS", "GOOGLE_ID"):
        drop_unique_on_column_if_any(bind, "USUARIOS", "GOOGLE_ID")
    if column_exists(bind, "USUARIOS", "ID_ROL"):
        drop_fk_on_column_if_any(bind, "USUARIOS", "ID_ROL")

    # Luego elimina columnas si existen
    with op.batch_alter_table("usuarios") as batch_op:
        if column_exists(bind, "USUARIOS", "GOOGLE_ID"):
            batch_op.drop_column("google_id")
        if column_exists(bind, "USUARIOS", "ID_ROL"):
            batch_op.drop_column("id_rol")

def downgrade():
    bind = op.get_bind()
    # Re-crea columnas (sin constraints automáticas; agrega si las necesitas)
    with op.batch_alter_table("usuarios") as batch_op:
        if not column_exists(bind, "USUARIOS", "ID_ROL"):
            batch_op.add_column(sa.Column("id_rol", sa.Integer(), nullable=True))
        if not column_exists(bind, "USUARIOS", "GOOGLE_ID"):
            batch_op.add_column(sa.Column("google_id", sa.String(255), nullable=True))

    # Si quieres devolver la UNIQUE y FK, créalas con nombres explícitos:
    # op.create_unique_constraint('uq_usuarios_google_id', 'usuarios', ['google_id'])
    # op.create_foreign_key('fk_usuarios_id_rol_roles', 'usuarios', 'roles', ['id_rol'], ['id'])
