"""Add role-permission associations.

Revision ID: 0003_role_permissions
Revises: 0002_user_auth
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_role_permissions"
down_revision = "0002_user_auth"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), primary_key=True),
        sa.Column(
            "permission_id",
            sa.Integer,
            sa.ForeignKey("permissions.id"),
            primary_key=True,
        ),
    )


def downgrade():
    op.drop_table("role_permissions")
