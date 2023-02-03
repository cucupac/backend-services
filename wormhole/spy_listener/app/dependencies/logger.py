import logging

from app.settings import settings
from app.usecases.interfaces.dependencies.logger import ILogger

logging.basicConfig(
    format="%(asctime)s|%(name)s|%(levelname)-5.5s|%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger(settings.application_name)
logger.setLevel(logging.INFO)

__all__ = ["logger"]


class Logger(ILogger):
    def debug(self, message: str, *args, **kwargs):
        logger.debug(message)

    def info(self, message: str, *args, **kwargs):
        logger.info(message)

    def warning(self, message: str, *args, **kwargs):
        logger.warning(message)

    def error(self, message: str, *args, **kwargs):
        logger.error(message)

    def critical(self, message: str, *args, **kwargs):
        logger.critical(message)


async def get_logger() -> ILogger:
    return Logger()
