# pylint: disable=duplicate-code

import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA
from app.infrastructure.db.models.tasks import TASKS
from app.settings import settings

BLOCK_RECORD = sa.Table(
    "block_record",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("task_id", sa.BigInteger, sa.ForeignKey(TASKS.c.id), nullable=False),
    sa.Column("chain_id", sa.Integer, nullable=False),
    sa.Column("last_scanned_block_number", sa.Integer, nullable=False),
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
    "ix_task_id_chain_id",
    BLOCK_RECORD.c.task_id,
    BLOCK_RECORD.c.chain_id,
    unique=True,
)
