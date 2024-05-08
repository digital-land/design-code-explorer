"""rename design code category

Revision ID: fdc3773fe529
Revises: 9fa5ce39c199
Create Date: 2024-05-08 10:32:08.904206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fdc3773fe529"
down_revision = "9fa5ce39c199"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table("design_code_category", "design_code_rule_category")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table("design_code_rule_category", "design_code_category")
    # ### end Alembic commands ###
