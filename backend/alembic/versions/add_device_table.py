"""Add device table for device-specific JWT tokens

Revision ID: add_device_table
Revises: 1593091087e6
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_device_table'
down_revision = '1593091087e6'
branch_labels = None
depends_on = None


def upgrade():
    # Create devices table
    op.create_table('devices',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('device_id', sa.String(36), nullable=False),
        sa.Column('device_name', sa.String(100), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('jwt_secret_key', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id')
    )
    
    # Add index for faster lookups
    op.create_index('ix_devices_device_id', 'devices', ['device_id'])
    op.create_index('ix_devices_user_id', 'devices', ['user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_devices_user_id', table_name='devices')
    op.drop_index('ix_devices_device_id', table_name='devices')
    
    # Drop devices table
    op.drop_table('devices')
