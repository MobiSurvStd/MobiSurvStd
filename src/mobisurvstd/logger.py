import sys

from loguru import logger


def setup(level: str = "INFO"):
    """Sets up loguru's logger with MobiSurvStd's format.

    This is called automatically when MobiSurvStd is used from the command line.

    When MobiSurvStd is used as a library, the logger is left untouched so that the calling
    application keeps full control over loguru's configuration (MobiSurvStd's messages are simply
    propagated to the handlers that the application defined).
    Call this function explicitly if you want MobiSurvStd's messages to be displayed the same way as
    in the command-line tool.

    Warning: this removes all the loguru handlers that were previously defined.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <level>{message}</level>",
        backtrace=False,
        diagnose=False,
        level=level,
    )
