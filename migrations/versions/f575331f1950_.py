"""Add/ensure column ROL on USUARIOS (Oracle-safe, idempotent)

Revision ID: f575331f1950
Revises: eb87058f884d
Create Date: 2025-09-02 14:58:15.611157
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f575331f1950"
down_revision = "eb87058f884d"
branch_labels = None
depends_on = None


# ---------- Helpers Oracle / SQLAlchemy 2.x ----------
def column_exists(bind, table, column, schema=None):
    """Return True if column exists (case-insensitive)."""
    insp = sa.inspect(bind)
    cols = insp.get_columns(table_name=table, schema=schema)
    return any(c["name"].upper() == column.upper() for c in cols)


def is_nullable(bind, table, column):
    """Return True if column is currently NULLABLE in Oracle."""
    row = bind.execute(
        sa.text(
            """
            SELECT NULLABLE
            FROM USER_TAB_COLS
            WHERE TABLE_NAME = :t AND COLUMN_NAME = :c
            """
        ),
        {"t": table.upper(), "c": column.upper()},
    ).fetchone()
    return bool(row and row[0] == "Y")


def upgrade():
    bind = op.get_bind()

    # 1) Agregar la columna si NO existe.
    #    En Oracle, si la tabla tiene filas y la queremos NOT NULL,
    #    primero la creamos como NULL con un default temporal.
    if not column_exists(bind, "USUARIOS", "ROL"):
        with op.batch_alter_table("usuarios") as batch_op:
            batch_op.add_column(
                sa.Column("rol", sa.String(50), nullable=True, server_default="user")
            )
        # Quitamos el default si no lo queremos permanente
        bind.exec_driver_sql("ALTER TABLE usuarios MODIFY (rol DEFAULT NULL)")

    # 2) Asegurar NOT NULL solo si hoy es NULLABLE
    if column_exists(bind, "USUARIOS", "ROL") and is_nullable(bind, "USUARIOS", "ROL"):
        bind.exec_driver_sql("ALTER TABLE usuarios MODIFY (rol NOT NULL)")


def downgrade():
    bind = op.get_bind()

    # Solo revertimos lo que hicimos en upgrade: eliminar la columna ROL si existe.
    if column_exists(bind, "USUARIOS", "ROL"):
        with op.batch_alter_table("usuarios") as batch_op:
            batch_op.drop_column("rol")
