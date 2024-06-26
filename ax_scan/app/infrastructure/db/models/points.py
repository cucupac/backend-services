# pylint: disable=duplicate-code

import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA
from app.settings import settings

POINTS = sa.Table(
    "points",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("account", sa.String, index=True, unique=True, nullable=False),
    sa.Column("points", sa.BigInteger, nullable=False),
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
