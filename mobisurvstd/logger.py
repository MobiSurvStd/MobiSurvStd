import sys

from loguru import logger


def setup():
    """Initializes logger."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <level>{message}</level>",
        backtrace=False,
        diagnose=False,
        level="INFO",
    )
