import logging

import env_logger
from env_logger import _handlers


def test_sparse_color_handler_accepts_missing_levelname() -> None:
    handler = _handlers.SparseColorHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.Logger("test")
    logger.addHandler(handler)
    env_logger._log_samples(logger)

def test_sparse_color_handler_accepts_basic_format() -> None:
    handler = _handlers.SparseColorHandler()
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logger = logging.Logger("test")
    logger.addHandler(handler)
    env_logger._log_samples(logger)