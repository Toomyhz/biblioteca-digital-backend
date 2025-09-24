"""empty message

Revision ID: 97c8d214c6dd
Revises: 496b15661793
Create Date: 2025-09-04 12:52:13.536284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97c8d214c6dd'
down_revision = '496b15661793'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SEQUENCE autores_seq START WITH 1 INCREMENT BY 1 NOCACHE")
    op.execute("CREATE SEQUENCE carreras_seq START WITH 1 INCREMENT BY 1 NOCACHE")
    op.execute("CREATE SEQUENCE libros_seq START WITH 1 INCREMENT BY 1 NOCACHE")
    op.execute("CREATE SEQUENCE usuario_id_seq START WITH 1 INCREMENT BY 1 NOCACHE")


def downgrade():
    op.execute("DROP SEQUENCE usuario_id_seq")
    op.execute("DROP SEQUENCE autores_seq")
    op.execute("DROP SEQUENCE libros_seq")
    op.execute("DROP SEQUENCE carreras_seq")
