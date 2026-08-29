"""add_admin_role_and_disputes

Revision ID: e7d45b64df72
Revises: 99e3ae4bdd66
Create Date: 2026-08-29 13:20:09.386778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e7d45b64df72'
down_revision: Union[str, Sequence[str], None] = '99e3ae4bdd66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add role column to users table if not exists
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    users_columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'role' not in users_columns:
        op.add_column('users', sa.Column('role', sa.String(length=20), server_default='USER', nullable=False))
        op.create_check_constraint('ck_user_role', 'users', "role IN ('USER', 'ADMIN')")

    # 2. Create disputes table if not exists
    tables = inspector.get_table_names()
    if 'disputes' not in tables:
        op.create_table(
            'disputes',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('transaction_id', sa.UUID(), nullable=False),
            sa.Column('sender_id', sa.UUID(), nullable=False),
            sa.Column('receiver_id', sa.UUID(), nullable=False),
            sa.Column('dispute_type', sa.String(length=30), nullable=False),
            sa.Column('status', sa.String(length=40), server_default='PENDING_RECEIVER_CONFIRMATION', nullable=False),
            sa.Column('reason', sa.Text(), nullable=False),
            sa.Column('receiver_notes', sa.Text(), nullable=True),
            sa.Column('admin_notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.CheckConstraint("dispute_type IN ('FALSE_TRANSACTION', 'FORMAL_COMPLAINT')", name='ck_dispute_type'),
            sa.CheckConstraint(
                "status IN ('PENDING_RECEIVER_CONFIRMATION', 'CONFIRMED_BY_RECEIVER', 'UNDER_INVESTIGATION', 'RESOLVED_REVERSED', 'REJECTED')",
                name='ck_dispute_status',
            ),
            sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_dispute_users', 'disputes', ['sender_id', 'receiver_id', 'status'], unique=False)
        op.create_index(op.f('ix_disputes_transaction_id'), 'disputes', ['transaction_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('disputes')
    op.drop_constraint('ck_user_role', 'users', type_='check')
    op.drop_column('users', 'role')
