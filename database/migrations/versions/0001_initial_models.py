"""Initial models migration

Revision ID: 0001_initial_models
Revises: None
Create Date: 2026-08-17
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(80), nullable=False, unique=True),
        sa.Column('email', sa.String(200), nullable=False, unique=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(80), nullable=False, unique=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # permissions
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(120), nullable=False, unique=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # user_roles association
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id'), nullable=False),
    )

    # cameras
    op.create_table(
        'cameras',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(120), nullable=False, unique=True),
        sa.Column('stream_url', sa.String(255), nullable=False),
        sa.Column('status', sa.String(30), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # zones
    op.create_table(
        'zones',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('camera_id', sa.Integer, sa.ForeignKey('cameras.id'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('polygon', sa.String(500), nullable=True),
        sa.Column('x', sa.Float, nullable=True),
        sa.Column('y', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # model_versions
    op.create_table(
        'model_versions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('version', sa.String(60), nullable=False),
        sa.Column('metrics', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # events
    op.create_table(
        'events',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('camera_id', sa.Integer, sa.ForeignKey('cameras.id'), nullable=False),
        sa.Column('event_type', sa.String(80), nullable=False, index=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # detections
    op.create_table(
        'detections',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('camera_id', sa.Integer, sa.ForeignKey('cameras.id'), nullable=False),
        sa.Column('track_id', sa.String(80), nullable=True),
        sa.Column('label', sa.String(80), nullable=False),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('x', sa.Float, nullable=True),
        sa.Column('y', sa.Float, nullable=True),
        sa.Column('width', sa.Float, nullable=True),
        sa.Column('height', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # tracks
    op.create_table(
        'tracks',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('camera_id', sa.Integer, sa.ForeignKey('cameras.id'), nullable=False),
        sa.Column('track_id', sa.String(80), nullable=False, unique=True),
        sa.Column('label', sa.String(80), nullable=False),
        sa.Column('status', sa.String(30), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
    )

    # alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('event_id', sa.Integer, sa.ForeignKey('events.id'), nullable=False),
        sa.Column('level', sa.String(30), nullable=True),
        sa.Column('message', sa.String(255), nullable=False),
        sa.Column('acknowledged', sa.Boolean, nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('alerts')
    op.drop_table('tracks')
    op.drop_table('detections')
    op.drop_table('events')
    op.drop_table('model_versions')
    op.drop_table('zones')
    op.drop_table('cameras')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
