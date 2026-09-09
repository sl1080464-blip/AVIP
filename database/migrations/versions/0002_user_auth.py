"""Add password hashes for user authentication.

Revision ID: 0002_user_auth
Revises: 0001_initial_models
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_user_auth"
down_revision = "0001_initial_models"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("users", "password_hash")
