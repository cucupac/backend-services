import sqlalchemy as sa
from sqlalchemy import CheckConstraint

from app.infrastructure.db.metadata import METADATA


EVM_TRANSACTIONS = sa.Table(
    "evm_transactions",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("chain_id", sa.Integer, nullable=False),
    sa.Column("transaction_hash", sa.String, nullable=False),
    sa.Column("block_hash", sa.String, nullable=False),
    sa.Column("block_number", sa.Integer, nullable=False),
    sa.Column("status", sa.Integer, nullable=False),
    CheckConstraint("status IN ('success', 'pending', 'failed')", name="check_status"),
    sa.Column("gas_price", sa.Integer, nullable=True),
    sa.Column("gas_used", sa.Integer, nullable=True),
    sa.Column("timestamp", sa.DateTime, nullable=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)
