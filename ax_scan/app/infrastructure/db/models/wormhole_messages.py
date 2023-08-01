# pylint: disable=duplicate-code
import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA
from app.infrastructure.db.models.cross_chain_transactions import (
    CROSS_CHAIN_TRANSACTIONS,
)
from app.settings import settings

WORMHOLE_MESSAGES = sa.Table(
    "wormhole_messages",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "cross_chain_transaction_id",
        sa.BigInteger,
        sa.ForeignKey(CROSS_CHAIN_TRANSACTIONS.c.id),
        index=True,
        unique=True,
        nullable=False,
    ),
    sa.Column("emitter_address", sa.String, nullable=False),
    sa.Column("source_chain_id", sa.Integer, nullable=False),
    sa.Column("sequence", sa.Integer, nullable=False),
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
    "ix_emitter_address_source_chain_id_sequence",
    WORMHOLE_MESSAGES.c.emitter_address,
    WORMHOLE_MESSAGES.c.source_chain_id,
    WORMHOLE_MESSAGES.c.sequence,
    unique=True,
)
