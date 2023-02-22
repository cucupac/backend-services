"""initial_schema

Revision ID: 0001
Revises: 
Create Date: 2023-02-22 14:24:04.310779

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
    op.create_table('fee_updates',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('chain_id', sa.Integer(), nullable=False),
    sa.Column('updates', sa.JSON(), nullable=False),
    sa.Column('transaction_hash', sa.String(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('emitter_address', sa.String(), nullable=True),
    sa.Column('from_address', sa.String(), nullable=True),
    sa.Column('to_address', sa.String(), nullable=True),
    sa.Column('source_chain_id', sa.Integer(), nullable=False),
    sa.Column('dest_chain_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=False),
    sa.Column('sequence', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_emitter_address_source_chain_id_sequence', 'transactions', ['emitter_address', 'source_chain_id', 'sequence'], unique=True)
    op.create_index(op.f('ix_transactions_from_address'), 'transactions', ['from_address'], unique=False)
    op.create_index(op.f('ix_transactions_to_address'), 'transactions', ['to_address'], unique=False)
    op.create_table('relays',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('message', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('transaction_hash', sa.String(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_relays_transaction_id'), 'relays', ['transaction_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_relays_transaction_id'), table_name='relays')
    op.drop_table('relays')
    op.drop_index(op.f('ix_transactions_to_address'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_from_address'), table_name='transactions')
    op.drop_index('ix_emitter_address_source_chain_id_sequence', table_name='transactions')
    op.drop_table('transactions')
    op.drop_table('fee_updates')
    # ### end Alembic commands ###