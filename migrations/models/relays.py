# pylint: disable=duplicate-code
import sqlalchemy as sa

from migrations.models.metadata import METADATA
from migrations.models.transactions import TRANSACTIONS

RELAYS = sa.Table(
    "relays",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "transaction_id",
        sa.BigInteger,
        sa.ForeignKey(TRANSACTIONS.c.id),
        index=True,
        unique=True,
        nullable=False,
    ),
    sa.Column("message", sa.String, nullable=True),
    sa.Column("status", sa.String, nullable=False, default="pending"),
    sa.Column("transaction_hash", sa.String, nullable=True),
    sa.Column("error", sa.Text(), nullable=True),
    sa.Column("cache_status", sa.String, nullable=False, default="never_cached"),
    sa.Column("grpc_status", sa.String, nullable=False, default="success"),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)
