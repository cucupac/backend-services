import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

TRANSACTIONS = sa.Table(
    "transactions",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("emitter_address", sa.String),
    sa.Column(
        "from_address",
        sa.String,
        index=True,
    ),
    sa.Column(
        "to_address",
        sa.String,
        index=True,
    ),
    sa.Column("source_chain_id", sa.Integer, nullable=False),
    sa.Column("dest_chain_id", sa.Integer, nullable=False),
    sa.Column("amount", sa.BigInteger, nullable=False),
    sa.Column("sequence", sa.BigInteger, nullable=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)


sa.Index(
    "ix_emitter_address_source_chain_id_sequence",
    TRANSACTIONS.c.emitter_address,
    TRANSACTIONS.c.source_chain_id,
    TRANSACTIONS.c.sequence,
    unique=True,
)
