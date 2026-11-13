"""Add WCAG version and level fields to violations

Revision ID: wcag22_fields
Revises: 
Create Date: 2026-11-13 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'wcag22_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add WCAG version and level columns to violations table
    op.add_column('violations', sa.Column('wcag_version', sa.String(10), server_default='2.2', nullable=False))
    op.add_column('violations', sa.Column('wcag_level', sa.String(3), server_default='AA', nullable=False))


def downgrade() -> None:
    # Remove WCAG version and level columns
    op.drop_column('violations', 'wcag_level')
    op.drop_column('violations', 'wcag_version')
