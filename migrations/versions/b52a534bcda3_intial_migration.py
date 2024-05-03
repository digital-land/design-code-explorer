"""intial migration

Revision ID: b52a534bcda3
Revises:
Create Date: 2024-05-03 14:26:54.361873

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b52a534bcda3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "organisation",
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("prefix", sa.Text(), nullable=True),
        sa.Column("reference", sa.Text(), nullable=True),
        sa.Column("statistical_geography", sa.Text(), nullable=True),
        sa.Column("geojson", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("organisation"),
    )
    op.create_table(
        "design_code",
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("organisation_id", sa.Text(), nullable=False),
        sa.Column("design_code_status", sa.Text(), nullable=True),
        sa.Column("documention_url", sa.Text(), nullable=True),
        sa.Column("document_url", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisation.organisation"],
        ),
        sa.PrimaryKeyConstraint("reference"),
    )
    op.create_table(
        "design_code_area",
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("geometry", sa.Text(), nullable=True),
        sa.Column("point", sa.Text(), nullable=True),
        sa.Column("organisation_id", sa.Text(), nullable=False),
        sa.Column("design_code_area_type", sa.Text(), nullable=True),
        sa.Column("design_code_reference", sa.Text(), nullable=False),
        sa.Column("design_code_rules", sa.Text(), nullable=True),
        sa.Column("documentation_url", sa.Text(), nullable=True),
        sa.Column("document_url", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["design_code_reference"],
            ["design_code.reference"],
        ),
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisation.organisation"],
        ),
        sa.PrimaryKeyConstraint("reference"),
    )
    op.create_table(
        "design_code_rule",
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("design_code_categories", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("organisation_id", sa.Text(), nullable=False),
        sa.Column("design_code_reference", sa.Text(), nullable=False),
        sa.Column("documentation_url", sa.Text(), nullable=True),
        sa.Column("document_url", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["design_code_reference"],
            ["design_code.reference"],
        ),
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisation.organisation"],
        ),
        sa.PrimaryKeyConstraint("reference"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("design_code_rule")
    op.drop_table("design_code_area")
    op.drop_table("design_code")
    op.drop_table("organisation")
    # ### end Alembic commands ###
