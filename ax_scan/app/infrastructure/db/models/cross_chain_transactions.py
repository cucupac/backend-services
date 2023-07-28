# pylint: disable=duplicate-code
import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA
from app.infrastructure.db.models.bridges import BRIDGES
from app.infrastructure.db.models.evm_transactions import EVM_TRANSACTIONS


CROSS_CHAIN_TRANSACTIONS = sa.Table(
    "cross_chain_transcations",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "bridge_id",
        sa.BigInteger,
        sa.ForeignKey(BRIDGES.c.id),
        unique=True,
        nullable=False,
    ),
    sa.Column("from_address", sa.String, index=True, nullable=True),
    sa.Column(
        "to_address",
        sa.String,
        index=True,
        nullable=True,
    ),
    sa.Column("source_chain_id", sa.Integer, nullable=False),
    sa.Column("dest_chain_id", sa.Integer, nullable=False),
    sa.Column("amount", sa.BigInteger, nullable=True),
    sa.Column(
        "source_chain_tx_id",
        sa.BigInteger,
        sa.ForeignKey(EVM_TRANSACTIONS.c.id),
        nullable=True,
    ),
    sa.Column(
        "dest_chain_tx_id",
        sa.BigInteger,
        sa.ForeignKey(EVM_TRANSACTIONS.c.id),
        nullable=True,
    ),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)
