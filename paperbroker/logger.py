import logging
import os
from datetime import datetime


def get_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        )
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(console_handler)

    return logger
