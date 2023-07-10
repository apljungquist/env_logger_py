from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List, Callable, Any, Dict, Iterable, Self, Tuple

import colorama

logger = logging.getLogger(__name__)


class ColorMap:
    @classmethod
    def dim_to_bright(cls) -> Self:
        return cls(
            [
                (logging.DEBUG, colorama.Style.DIM),
                (logging.INFO, colorama.Style.NORMAL),
                (logging.WARNING, colorama.Style.NORMAL + colorama.Fore.YELLOW),
                (logging.ERROR, colorama.Style.NORMAL + colorama.Fore.RED),
                (logging.CRITICAL, colorama.Style.BRIGHT + colorama.Fore.RED),
            ]
        )

    def __init__(self, styles: Iterable[Tuple[int, str]]) -> None:
        self._styles = list(styles)

    def color(self, level: int) -> str:
        for l, s in self._styles:
            if level <= l:
                return s
        return ""

    def colored(self, level: int, text: str) -> str:
        return self.color(level) + text + colorama.Style.RESET_ALL


class Handler(logging.StreamHandler):
    def __init__(self, *args, **kwargs) -> None:
        self._style_output = kwargs.pop("style_output", True)
        self._color_map = ColorMap.dim_to_bright()
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        default = super().format(record)
        # TODO: Consider making configurable
        escaped = json.dumps(default)[1:-1]
        # TODO: Consider styling unnamed levels
        colored = (
            self._color_map.colored(record.levelno, escaped)
            if self._style_output
            else escaped
        )
        return colored


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
    raise ValueError(f"Invalid log handler: {text}")


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
        lambda: "%(asctime)s %(levelname)s %(message)s",
    )
    _resolve(
        kwargs,
        "level",
        lambda: _valid_level(os.environ.get("LOG_LEVEL")),
        lambda: "INFO",
    )
    _resolve(
        kwargs,
        "handlers",
        lambda: _valid_handlers(os.environ.get("LOG_HANDLER")),
        lambda: [Handler(style_output=_style_output())],
    )
    logging.basicConfig(**kwargs)


def _demo() -> None:
    logger.debug("A debug message")
    logger.info("An info message")
    logger.info(
        "Another info message. This one contains special characters: \n\t\r\b\f\v\a..."
    )
    logger.warning("A warning message")
    logger.error("An error message")
    logger.critical("A critical message")
    try:
        raise Exception("Oops")
    except Exception:
        logger.exception("A exception message")


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
