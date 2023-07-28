from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskName(str, Enum):
    GATHER_TRANSACTIONS = "gather_transactions"
    VERIFY_TRANSACTIONS = "verify_transactions"


class TaskInDb(BaseModel):
    id: int = Field(
        ...,
        description="The database-assigned uinque identifier for a given cron job.",
        example=1,
    )
    name: TaskName = Field(
        ...,
        description="The unique name of the cron job.",
        example="retry_failed",
    )
    created_at: datetime = Field(
        ...,
        description="The time that the transaction object was created.",
        example="2020-02-11 17:47:44.170522",
    )
    updated_at: datetime = Field(
        ...,
        description="The time that the transaction object was updated.",
        example="2020-02-11 17:47:44.170522",
    )


class TaskLockInDb(BaseModel):
    id: int = Field(
        ...,
        description="The database-assigned uinque identifier for a given lock.",
        example=1,
    )
    task_id: int = Field(
        ...,
        description="The foreign key identifier that links locks to tasks.",
        example=1,
    )
    created_at: datetime = Field(
        ...,
        description="The time that the transaction object was created.",
        example="2020-02-11 17:47:44.170522",
    )
    updated_at: datetime = Field(
        ...,
        description="The time that the transaction object was updated.",
        example="2020-02-11 17:47:44.170522",
    )
