from enum import Enum


class Status(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
