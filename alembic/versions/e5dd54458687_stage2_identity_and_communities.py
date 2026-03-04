"""stage2: identity and communities

Revision ID: e5dd54458687
Revises: 277bb65921e9
Create Date: 2026-03-03 20:04:33.716261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5dd54458687'
down_revision: Union[str, Sequence[str], None] = '277bb65921e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- New tables ---
    op.create_table('communities',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('display_name', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['agents.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table('sessions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('agent_id', sa.Uuid(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_sessions_agent', 'sessions', ['agent_id'], unique=False)
    op.create_index('idx_sessions_expiry', 'sessions', ['expires_at'], unique=False)
    op.create_table('community_members',
        sa.Column('community_id', sa.Uuid(), nullable=False),
        sa.Column('agent_id', sa.Uuid(), nullable=False),
        sa.Column('role', sa.String(length=16), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id']),
        sa.ForeignKeyConstraint(['community_id'], ['communities.id']),
        sa.PrimaryKeyConstraint('community_id', 'agent_id'),
    )
    op.create_index(op.f('ix_community_members_agent_id'), 'community_members', ['agent_id'], unique=False)

    # --- agents: new identity columns ---
    op.add_column('agents', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('agents', sa.Column('password_hash', sa.String(length=128), nullable=True))
    op.add_column('agents', sa.Column('owner_id', sa.Uuid(), nullable=True))
    op.add_column('agents', sa.Column('claim_token_hash', sa.String(length=64), nullable=True))
    op.add_column('agents', sa.Column('claim_token_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('agents', sa.Column('claim_status', sa.String(length=16),
                                       server_default=sa.text("'unclaimed'"), nullable=False))
    op.alter_column('agents', 'api_key_hash',
                    existing_type=sa.VARCHAR(length=64),
                    nullable=True)
    op.create_foreign_key('fk_agents_owner_id', 'agents', 'agents', ['owner_id'], ['id'])
    op.create_index(
        'idx_agents_email',
        'agents',
        ['email'],
        unique=True,
        postgresql_where=sa.text('email IS NOT NULL'),
    )

    # --- questions: community_id ---
    op.add_column('questions', sa.Column('community_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_questions_community_id', 'questions', 'communities', ['community_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # --- questions ---
    op.drop_constraint('fk_questions_community_id', 'questions', type_='foreignkey')
    op.drop_column('questions', 'community_id')

    # --- agents ---
    op.drop_index('idx_agents_email', table_name='agents', postgresql_where=sa.text('email IS NOT NULL'))
    op.drop_constraint('fk_agents_owner_id', 'agents', type_='foreignkey')
    op.alter_column('agents', 'api_key_hash',
                    existing_type=sa.VARCHAR(length=64),
                    nullable=False)
    op.drop_column('agents', 'claim_status')
    op.drop_column('agents', 'claim_token_expires_at')
    op.drop_column('agents', 'claim_token_hash')
    op.drop_column('agents', 'owner_id')
    op.drop_column('agents', 'password_hash')
    op.drop_column('agents', 'email')

    # --- new tables ---
    op.drop_index(op.f('ix_community_members_agent_id'), table_name='community_members')
    op.drop_table('community_members')
    op.drop_index('idx_sessions_expiry', table_name='sessions')
    op.drop_index('idx_sessions_agent', table_name='sessions')
    op.drop_table('sessions')
    op.drop_table('communities')
