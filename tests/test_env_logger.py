import logging
from typing import Type

import pytest

import env_logger
from env_logger import _handlers


# This test serves two purposes:
# 1. a smoke test ensuring that handlers don't crash with common configuration,
# 2. a gallery of what common configurations look like.
@pytest.mark.parametrize(
    "format_",
    [
        logging.BASIC_FORMAT,
        logging.PercentStyle.default_format,
        env_logger._default_format(),
    ],
)
@pytest.mark.parametrize(
    "handler_cls",
    [
        _handlers.SparseColorHandler,
        _handlers.Handler,
        _handlers.RichHandler,
    ],
)
def test_handler_accept_formats(
    handler_cls: Type[logging.StreamHandler], format_: str
) -> None:
    handler = handler_cls()
    handler.setFormatter(logging.Formatter(format_))
    logger = logging.Logger("test")
    logger.addHandler(handler)

    env_logger._log_samples(logger)


@pytest.mark.parametrize(
    "handler_cls",
    [
        _handlers.SparseColorHandler,
        _handlers.Handler,
        _handlers.RichHandler,
    ],
)
def test_handler_uses_stderr(capsys, handler_cls: Type[logging.StreamHandler]) -> None:
    handler = handler_cls()
    logger = logging.Logger("test")
    logger.addHandler(handler)

    env_logger._log_samples(logger)

    captured = capsys.readouterr()
    assert captured.err and not captured.out
