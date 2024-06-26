"""rename design code rule column name

Revision ID: 42c2405d38eb
Revises: 943862691157
Create Date: 2024-05-08 14:44:23.317022

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "42c2405d38eb"
down_revision = "943862691157"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "design_code_rule",
        "design_code_categories",
        nullable=True,
        new_column_name="design_code_rule_categories",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "design_code_rule",
        "design_code_rule_categories",
        nullable=True,
        new_column_name="design_code_categories",
    )
    # ### end Alembic commands ###
