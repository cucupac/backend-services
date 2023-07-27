"""Initial Schema

Revision ID: 0001
Revises: 
Create Date: 2023-07-19 23:02:45.907516

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
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='gas_system'
    )
    op.create_table('mock_transactions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('chain_id', sa.Integer(), nullable=False),
    sa.Column('payload', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='gas_system'
    )
    op.create_table('tasks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='gas_system'
    )
    op.create_index(op.f('ix_gas_system_tasks_name'), 'tasks', ['name'], unique=True, schema='gas_system')
    op.create_table('task_locks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['gas_system.tasks.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='gas_system'
    )
    op.create_index(op.f('ix_gas_system_task_locks_task_id'), 'task_locks', ['task_id'], unique=True, schema='gas_system')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gas_system_task_locks_task_id'), table_name='task_locks', schema='gas_system')
    op.drop_table('task_locks', schema='gas_system')
    op.drop_index(op.f('ix_gas_system_tasks_name'), table_name='tasks', schema='gas_system')
    op.drop_table('tasks', schema='gas_system')
    op.drop_table('mock_transactions', schema='gas_system')
    op.drop_table('fee_updates', schema='gas_system')
    # ### end Alembic commands ###