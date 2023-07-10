from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import TYPE_CHECKING

from . import _handlers

if TYPE_CHECKING:
    from typing import Optional, List, Callable, Any, Dict


def _resolve(
    kwargs: Dict[str, Any],
    key: str,
    from_env: Callable[[], Any],
    default: Callable[[], Any],
) -> List[str]:
    from_env = from_env()
    if from_env is not None:
        kwargs[key] = from_env
    if key not in kwargs:
        kwargs[key] = default()
    return []


def _valid_level(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    if text not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"Invalid log level: {text}")
    return text


def _valid_format(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    formatter = logging.Formatter(text)
    try:
        formatter.format(
            logging.LogRecord("name", logging.INFO, "pathname", 0, "msg", (), None)
        )
    except Exception as e:
        raise ValueError(f"Invalid log format: {text}") from e
    return text


def _valid_handlers(text: Optional[str]) -> Optional[List[logging.Handler]]:
    if text is None:
        return None
    if text == "rich":
        try:
            import rich.logging  # type: ignore

            return [rich.logging.RichHandler()]
        except ImportError as e:
            raise ValueError(
                f"Invalid log handler: {text} (install rich to enable this handler)"
            ) from e
    if text == "sparse":
        return [_handlers.SparseColorHandler()]
    raise ValueError(f"Invalid log handler: {text}")


def _default_format() -> str:
    return "%(asctime)s %(levelname)s %(message)s"


def _default_level() -> str:
    return "INFO"


def _default_handlers() -> List[logging.Handler]:
    return [_handlers.Handler(style_output=_style_output())]


def _style_output() -> bool:
    # Inspired by https://clig.dev/#output
    # But I disagree with the authors on using stderr for logging.
    if not sys.stderr.isatty():
        return False
    if os.environ.get("NO_COLOR", "0") != "0":
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return True


def configure(**kwargs) -> None:
    _resolve(
        kwargs,
        "format",
        lambda: _valid_format(os.environ.get("LOG_FORMAT")),
        _default_format,
    )
    _resolve(
        kwargs,
        "level",
        lambda: _valid_level(os.environ.get("LOG_LEVEL")),
        _default_level,
    )
    _resolve(
        kwargs,
        "handlers",
        lambda: _valid_handlers(os.environ.get("LOG_HANDLER")),
        _default_handlers,
    )
    logging.basicConfig(**kwargs)


def _log_samples(logger: logging.Logger) -> None:
    logger.debug("A debug message")
    logger.info("An info message")
    logger.warning("A warning message")
    logger.error("An error message")
    logger.critical("A critical message")
    try:
        raise Exception("Oops")
    except Exception:
        logger.exception("A exception message")


def _demo() -> None:
    _log_samples(logging.getLogger(__name__))


def _parser() -> argparse.ArgumentParser:
    root_parser = argparse.ArgumentParser(
        "env_logger",
        "Utility for configuring the Python logging module via environment variables.",
    )
    subparsers = root_parser.add_subparsers(required=True)

    demo_parser = subparsers.add_parser("demo")
    demo_parser.set_defaults(func=_demo)
    return root_parser


def _main() -> None:
    configure()
    parser = _parser()
    args = parser.parse_args()
    args.func()
