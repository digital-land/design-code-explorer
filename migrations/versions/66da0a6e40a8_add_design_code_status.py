"""add design code status

Revision ID: 66da0a6e40a8
Revises: a427dc28b534
Create Date: 2024-05-07 11:48:33.974576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "66da0a6e40a8"
down_revision = "a427dc28b534"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "design_code_status",
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("entity", sa.INTEGER(), nullable=True),
        sa.Column("prefix", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("reference"),
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("design_code_status")
    # ### end Alembic commands ###
