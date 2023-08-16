# pylint: disable=duplicate-code
import sqlalchemy as sa
from sqlalchemy import CheckConstraint

from app.infrastructure.db.metadata import METADATA
from app.infrastructure.db.models.evm_transactions import EVM_TRANSACTIONS
from app.settings import settings

CROSS_CHAIN_TRANSACTIONS = sa.Table(
    "cross_chain_transactions",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("bridge", sa.String, nullable=False),
    CheckConstraint("bridge IN ('wormhole', 'layer_zero')", name="check_bridge"),
    sa.Column("from_address", sa.String, index=True, nullable=True),
    sa.Column(
        "to_address",
        sa.String,
        index=True,
        nullable=True,
    ),
    sa.Column("source_chain_id", sa.Integer, nullable=False),
    sa.Column("dest_chain_id", sa.Integer, nullable=False),
    sa.Column("amount", sa.BigInteger, nullable=False),
    sa.Column(
        "source_chain_tx_id",
        sa.BigInteger,
        sa.ForeignKey(EVM_TRANSACTIONS.c.id),
        nullable=True,
        unique=True,
    ),
    sa.Column(
        "dest_chain_tx_id",
        sa.BigInteger,
        sa.ForeignKey(EVM_TRANSACTIONS.c.id),
        nullable=True,
        unique=True,
    ),
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
