"""agregar secuencia autores

Revision ID: 2e12492b7549
Revises: 78801c6dcb35
Create Date: 2025-09-02 20:55:00.935463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e12492b7549'
down_revision = '78801c6dcb35'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SEQUENCE autores_seq START WITH 1 INCREMENT BY 1 NOCACHE")
    op.execute("CREATE SEQUENCE carreras_seq START WITH 1 INCREMENT BY 1 NOCACHE")

def downgrade():
    op.execute("DROP SEQUENCE carreras_seq")
    op.execute("DROP SEQUENCE autores_seq")
