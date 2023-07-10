from __future__ import annotations

import copy
import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Iterable, Self, Tuple

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

    @classmethod
    def dim_to_back(cls) -> Self:
        return cls(
            [
                (logging.DEBUG, colorama.Style.DIM),
                (logging.INFO, colorama.Style.BRIGHT),
                (logging.WARNING, colorama.Style.BRIGHT + colorama.Fore.YELLOW),
                (logging.ERROR, colorama.Style.BRIGHT + colorama.Fore.RED),
                (
                    logging.CRITICAL,
                    colorama.Style.BRIGHT + colorama.Fore.WHITE + colorama.Back.RED,
                ),
            ]
        )

    @classmethod
    def dim_or_normal(cls) -> Self:
        return cls(
            [
                (logging.DEBUG, colorama.Style.DIM),
                (logging.CRITICAL, colorama.Style.NORMAL),
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


def _without_exc_info(record: logging.LogRecord) -> logging.LogRecord:
    record = copy.copy(record)
    record.exc_info = None
    return record


class SparseColorFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs) -> None:
        fmt: str = kwargs.pop("fmt")
        left, middle, right = fmt.rpartition("%(levelname)s")

        kwargs["fmt"] = left  # makes mypy happy
        self._left = logging.Formatter(*args, **kwargs) if left else None
        self._middle = middle
        kwargs["fmt"] = right
        self._right = logging.Formatter(*args, **kwargs)

        self._level_color_map = ColorMap.dim_to_back()
        self._other_color_map = ColorMap.dim_or_normal()
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        level_style = self._level_color_map.color(record.levelno)
        other_style = self._other_color_map.color(record.levelno)
        record_without_exc_info = _without_exc_info(record)
        # TODO: Consider optimizing
        return str(
            (
                other_style
                + (
                    json.dumps(self._left.format(record_without_exc_info))[1:-1]
                    if self._left
                    else ""
                )
                + colorama.Style.RESET_ALL
                + level_style
                + (record.levelname if self._middle else "")
                + colorama.Style.RESET_ALL
                + other_style
                + (json.dumps(self._right.format(record))[1:-1])
                + colorama.Style.RESET_ALL
            )
        )


class SparseColorHandler(logging.StreamHandler):
    def setFormatter(self, fmt: Optional[logging.Formatter]) -> None:
        if fmt is not None:
            fmt = SparseColorFormatter(fmt=fmt._fmt)
        super().setFormatter(fmt)
