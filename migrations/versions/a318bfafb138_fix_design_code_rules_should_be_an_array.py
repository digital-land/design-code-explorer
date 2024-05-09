"""fix design_code_rules. should be an array

Revision ID: a318bfafb138
Revises: 42c2405d38eb
Create Date: 2024-05-09 08:45:40.022605

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a318bfafb138"
down_revision = "42c2405d38eb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_column("design_code_area", "design_code_rules")
    op.add_column(
        "design_code_area",
        sa.Column("design_code_rules", postgresql.ARRAY(sa.Text()), nullable=True),
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("design_code_area", "design_code_rules")
    op.add_column(
        "design_code_area",
        sa.Column("design_code_rules", sa.Text(), nullable=True),
    )

    # ### end Alembic commands ###