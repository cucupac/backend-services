# pylint: disable=duplicate-code
import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

from app.settings import settings

FEE_UPDATES = sa.Table(
    "fee_updates",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("chain_id", sa.Integer, nullable=False),
    sa.Column("updates", sa.JSON, nullable=False),
    sa.Column("transaction_hash", sa.String, nullable=True),
    sa.Column("status", sa.String, nullable=False, default="failed"),
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
