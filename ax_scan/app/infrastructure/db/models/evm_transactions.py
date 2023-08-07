import sqlalchemy as sa
from sqlalchemy import CheckConstraint

from app.infrastructure.db.metadata import METADATA
from app.settings import settings

EVM_TRANSACTIONS = sa.Table(
    "evm_transactions",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("chain_id", sa.Integer, nullable=False),
    sa.Column("transaction_hash", sa.String, nullable=False),
    sa.Column("block_hash", sa.String, nullable=False),
    sa.Column("block_number", sa.Integer, nullable=False),
    sa.Column("gas_price", sa.BigInteger, nullable=True),
    sa.Column("gas_used", sa.Integer, nullable=True),
    sa.Column("status", sa.String, nullable=False),
    CheckConstraint("status IN ('success', 'pending', 'failed')", name="check_status"),
    sa.Column("error", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
    schema=settings.db_schema,
)


sa.Index(
    "ix_transaction_hash_chain_id",
    EVM_TRANSACTIONS.c.transaction_hash,
    EVM_TRANSACTIONS.c.chain_id,
    unique=True,
)
