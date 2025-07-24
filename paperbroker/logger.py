import logging
import os
from datetime import datetime


class FixFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, str):
            record.msg = record.msg.replace("\x01", "|")
        return super().format(record)


def get_logger(
    name: str, log_dir: str = "logs", console: bool = True
) -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent adding multiple handlers when reused
    if not logger.handlers:
        formatter = FixFormatter("[%(asctime)s] [%(levelname)s] %(message)s")

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Optional console handler
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(FixFormatter("[%(levelname)s] %(message)s"))
            logger.addHandler(console_handler)

    return logger
