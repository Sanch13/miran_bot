import sys

from loguru import logger
import os


if not os.path.exists('logs'):
    os.makedirs('logs')

logger.remove()

logger.add("logs/logs.log", rotation="10 MB", retention="10 days", compression="zip")
