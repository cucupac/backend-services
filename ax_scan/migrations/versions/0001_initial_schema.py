"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2023-08-07 15:15:12.119673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('evm_transactions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('chain_id', sa.Integer(), nullable=False),
    sa.Column('transaction_hash', sa.String(), nullable=False),
    sa.Column('block_hash', sa.String(), nullable=False),
    sa.Column('block_number', sa.Integer(), nullable=False),
    sa.Column('gas_price', sa.BigInteger(), nullable=True),
    sa.Column('gas_used', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('success', 'pending', 'failed')", name='check_status'),
    sa.PrimaryKeyConstraint('id'),
    schema='ax_scan'
    )
    op.create_index('ix_transaction_hash_chain_id', 'evm_transactions', ['transaction_hash', 'chain_id'], unique=True, schema='ax_scan')
    op.create_table('tasks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='ax_scan'
    )
    op.create_index(op.f('ix_ax_scan_tasks_name'), 'tasks', ['name'], unique=True, schema='ax_scan')
    op.create_table('cross_chain_transactions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('bridge', sa.String(), nullable=False),
    sa.Column('from_address', sa.String(), nullable=True),
    sa.Column('to_address', sa.String(), nullable=True),
    sa.Column('source_chain_id', sa.Integer(), nullable=False),
    sa.Column('dest_chain_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=True),
    sa.Column('source_chain_tx_id', sa.BigInteger(), nullable=True),
    sa.Column('dest_chain_tx_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("bridge IN ('wormhole', 'layer_zero')", name='check_bridge'),
    sa.ForeignKeyConstraint(['dest_chain_tx_id'], ['ax_scan.evm_transactions.id'], ),
    sa.ForeignKeyConstraint(['source_chain_tx_id'], ['ax_scan.evm_transactions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dest_chain_tx_id'),
    sa.UniqueConstraint('source_chain_tx_id'),
    schema='ax_scan'
    )
    op.create_index(op.f('ix_ax_scan_cross_chain_transactions_from_address'), 'cross_chain_transactions', ['from_address'], unique=False, schema='ax_scan')
    op.create_index(op.f('ix_ax_scan_cross_chain_transactions_to_address'), 'cross_chain_transactions', ['to_address'], unique=False, schema='ax_scan')
    op.create_table('task_locks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['ax_scan.tasks.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='ax_scan'
    )
    op.create_index(op.f('ix_ax_scan_task_locks_task_id'), 'task_locks', ['task_id'], unique=True, schema='ax_scan')
    op.create_table('layer_zero_messages',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('cross_chain_tx_id', sa.BigInteger(), nullable=False),
    sa.Column('emitter_address', sa.String(), nullable=False),
    sa.Column('source_chain_id', sa.Integer(), nullable=False),
    sa.Column('dest_chain_id', sa.Integer(), nullable=False),
    sa.Column('nonce', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['cross_chain_tx_id'], ['ax_scan.cross_chain_transactions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='ax_scan'
    )
    op.create_index(op.f('ix_ax_scan_layer_zero_messages_cross_chain_tx_id'), 'layer_zero_messages', ['cross_chain_tx_id'], unique=True, schema='ax_scan')
    op.create_index('ix_emitter_address_source_chain_id_dest_chain_id_nonce', 'layer_zero_messages', ['emitter_address', 'source_chain_id', 'dest_chain_id', 'nonce'], unique=True, schema='ax_scan')
    op.create_table('wormhole_messages',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('cross_chain_tx_id', sa.BigInteger(), nullable=False),
    sa.Column('emitter_address', sa.String(), nullable=False),
    sa.Column('source_chain_id', sa.Integer(), nullable=False),
    sa.Column('sequence', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['cross_chain_tx_id'], ['ax_scan.cross_chain_transactions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='ax_scan'
    )
    op.create_index(op.f('ix_ax_scan_wormhole_messages_cross_chain_tx_id'), 'wormhole_messages', ['cross_chain_tx_id'], unique=True, schema='ax_scan')
    op.create_index('ix_emitter_address_source_chain_id_sequence', 'wormhole_messages', ['emitter_address', 'source_chain_id', 'sequence'], unique=True, schema='ax_scan')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_emitter_address_source_chain_id_sequence', table_name='wormhole_messages', schema='ax_scan')
    op.drop_index(op.f('ix_ax_scan_wormhole_messages_cross_chain_tx_id'), table_name='wormhole_messages', schema='ax_scan')
    op.drop_table('wormhole_messages', schema='ax_scan')
    op.drop_index('ix_emitter_address_source_chain_id_dest_chain_id_nonce', table_name='layer_zero_messages', schema='ax_scan')
    op.drop_index(op.f('ix_ax_scan_layer_zero_messages_cross_chain_tx_id'), table_name='layer_zero_messages', schema='ax_scan')
    op.drop_table('layer_zero_messages', schema='ax_scan')
    op.drop_index(op.f('ix_ax_scan_task_locks_task_id'), table_name='task_locks', schema='ax_scan')
    op.drop_table('task_locks', schema='ax_scan')
    op.drop_index(op.f('ix_ax_scan_cross_chain_transactions_to_address'), table_name='cross_chain_transactions', schema='ax_scan')
    op.drop_index(op.f('ix_ax_scan_cross_chain_transactions_from_address'), table_name='cross_chain_transactions', schema='ax_scan')
    op.drop_table('cross_chain_transactions', schema='ax_scan')
    op.drop_index(op.f('ix_ax_scan_tasks_name'), table_name='tasks', schema='ax_scan')
    op.drop_table('tasks', schema='ax_scan')
    op.drop_index('ix_transaction_hash_chain_id', table_name='evm_transactions', schema='ax_scan')
    op.drop_table('evm_transactions', schema='ax_scan')
    # ### end Alembic commands ###