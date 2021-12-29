import logging
from logging import Logger
import sys
from typing import Optional


def init_logger(log_file_path: Optional[str] = None,
log_file_level: int =logging.NOTSET, name: Optional[str]= None) -> Logger:
    """Basic logger for fluke framework."""
    log_format = logging.Formatter("[%(asctime)s] %(message)s")
    if name is None:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.handlers = [console_handler]

    if log_file_path is not None:
        file_handler = logging.FileHandler(log_file_path, mode = 'w')
        file_handler.setLevel(log_file_level)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    return logger