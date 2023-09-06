# pylint: disable=duplicate-code

import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA
from app.infrastructure.db.models.evm_transactions import EVM_TRANSACTIONS
from app.settings import settings

MINTS = sa.Table(
    "mints",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "chain_tx_id",
        sa.BigInteger,
        sa.ForeignKey(EVM_TRANSACTIONS.c.id),
        nullable=True,
        unique=True,
    ),
    sa.Column("account", sa.String, index=True, nullable=False),
    sa.Column("amount", sa.Numeric, nullable=False),
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
