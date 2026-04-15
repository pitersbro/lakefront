import sys

from loguru import logger

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
            "level": "INFO",
            "colorize": True,
            "format": ("<level>{level: <8}</level> | {message}"),
        },
    ],
    "extra": {"app_name": "my_project"},
}

logger.configure(**config)
