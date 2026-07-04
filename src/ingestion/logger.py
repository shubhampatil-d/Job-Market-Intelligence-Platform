"""
Logging Configuration

Centralized logger for the ingestion layer.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a logger instance.
    """

    logger = logging.getLogger(name)

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger