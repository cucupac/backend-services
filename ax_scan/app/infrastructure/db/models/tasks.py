# pylint: disable=duplicate-code
import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

TASKS = sa.Table(
    "tasks",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("name", sa.String, nullable=False, unique=True, index=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)


TASK_LOCKS = sa.Table(
    "task_locks",
    METADATA,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column(
        "task_id",
        sa.BigInteger,
        sa.ForeignKey(TASKS.c.id),
        unique=True,
        index=True,
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
