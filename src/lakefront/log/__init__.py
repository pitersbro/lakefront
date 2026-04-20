import os
import sys

from loguru import logger

LOG_LEVEL = os.getenv("LAKEFRONT_LOG_LEVEL", "DEBUG").upper()


logger.level("TRACE", color="<blue>")
logger.level("DEBUG", color="<cyan>")
logger.level("INFO", color="<green>")
logger.level("SUCCESS", color="<bold><green>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.level("CRITICAL", color="<bold><red>")

config = {
    "handlers": [
        {
            "sink": sys.stderr,
            "level": LOG_LEVEL,
            "colorize": True,
            "format": ("<level>{level: <8}</level> | {message}"),
        },
    ],
    "extra": {"app_name": "my_project"},
}

logger.configure(**config)


def configure_for_tui(log_path: str) -> None:
    """Replace the stderr sink with a file sink for TUI mode."""
    logger.remove()
    logger.add(
        log_path,
        level=LOG_LEVEL,
        colorize=False,
        format="{time:HH:mm:ss} | {level: <8} | {message}",
    )
