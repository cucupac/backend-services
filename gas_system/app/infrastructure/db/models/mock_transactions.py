import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA
from app.settings import settings

MOCK_TRANSACTIONS = sa.Table(
    "mock_transactions",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("chain_id", sa.Integer, nullable=False),
    sa.Column("payload", sa.String, nullable=True),
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
