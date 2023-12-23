#!/usr/bin/env python3
from __future__ import annotations

import collections
import dataclasses
import logging
import re
import sys
from typing import (
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

logger = logging.getLogger(__name__)

_T = TypeVar("_T")

_TargetsT = Dict[str, str]
_SubsectionsT = Dict[Optional[str], _TargetsT]
_SectionsT = Dict[Optional[str], _SubsectionsT]


class Overline(str):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"


class Section(str):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"


class Subsection(str):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"


class Target(str):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"


class Stream(Generic[_T]):
    def __init__(self, iterator: Iterable[_T]) -> None:
        self._iterator = iter(iterator)
        self._buffer: collections.deque[_T] = collections.deque()

    def __getitem__(self, item: int) -> _T:
        while len(self._buffer) <= item:
            try:
                self._buffer.append(next(self._iterator))
            except StopIteration as e:
                raise IndexError from e

        return self._buffer[item]

    def pop(self) -> _T:
        if self._buffer:
            result = self._buffer.popleft()
        else:
            try:
                result = next(self._iterator)
            except StopIteration as e:
                raise IndexError from e
        return result


@dataclasses.dataclass(frozen=True)
class Docstring:
    lines: List[str]
    ref: Union[Overline, Section, Subsection, Target]
    _target_pat: ClassVar[re.Pattern] = re.compile(
        r"^(?P<name>[a-zA-Z0-9_.-]+(/[a-zA-Z0-9_.-]+)*):.*$"
    )

    @staticmethod
    def _summary_from_target(name: str) -> str:
        return name.capitalize().replace("_", " ")

    @staticmethod
    def _is_overline(lines: Sequence[str]) -> bool:
        """Return True iff lines represent an overline

        >>> Docstring._is_overline(['Makefile', '********'])
        True
        """
        return 1 < len(lines) and set(lines[1]) == {"*"}

    @staticmethod
    def _is_section(lines: Sequence[str]) -> bool:
        """Return True iff lines represent a section

        >>> Docstring._is_section(['Configuration', '============='])
        True
        >>> Docstring._is_section(['Configuration'])
        False
        """
        return 1 < len(lines) and set(lines[1]) == {"="}

    @staticmethod
    def _is_subsection(lines: Sequence[str]) -> bool:
        return 1 < len(lines) and set(lines[1]) == {"-"}

    @classmethod
    def take_one(cls, stream: Stream[str]) -> Docstring:
        while not stream[0].startswith("##"):
            stream.pop()

        lines = []
        while stream[0].startswith("##"):
            lines.append(stream.pop()[2:].strip())

        if cls._is_overline(lines):
            ref: Union[Overline, Section, Subsection, Target] = Overline(lines[0])
        elif cls._is_section(lines):
            ref = Section(lines[0])
        elif cls._is_subsection(lines):
            ref = Subsection(lines[0])
        elif m := cls._target_pat.match(stream[0]):
            stream.pop()
            ref = Target(m.group("name"))
            if lines == ["_"]:
                lines = [cls._summary_from_target(ref)]
        else:
            logger.debug("Lines %r", lines)
            logger.debug("Stream head %r", stream[0])
            raise RuntimeError("Could not parse a ref")

        return Docstring(lines, ref)

    @classmethod
    def take_all(cls, stream: Stream[str]) -> List[Docstring]:
        result = []
        while True:
            try:
                result.append(Docstring.take_one(stream))
            except IndexError:
                break
        return result


class Formatter:
    @classmethod
    def lines(cls, docstrings: Iterable[Docstring]) -> Iterator[str]:
        # pylint: disable=unused-argument
        # ... because subclasses do use it
        yield ""
        raise NotImplementedError

    @classmethod
    def print(cls, docstrings: Iterable[Docstring]) -> None:
        print("\n".join(cls.lines(docstrings)))


class HelpFormatter(Formatter):
    @staticmethod
    def _hierarchy(docstrings: Iterable[Docstring]) -> _SectionsT:
        targets: _TargetsT = {}
        subsections: _SubsectionsT = {None: targets}
        sections: _SectionsT = {None: subsections}

        for docstring in docstrings:
            ref = docstring.ref
            if isinstance(ref, Overline):
                logger.debug("Sections %r", sections)
                assert sections == {
                    None: {None: {}}
                }, "Expected an overline only at the start of the document"
            elif isinstance(ref, Section):
                assert ref not in sections
                targets = {}
                subsections = {None: targets}
                sections[ref] = subsections
            elif isinstance(ref, Subsection):
                assert ref not in subsections
                targets = {}
                subsections[ref] = targets
            elif isinstance(ref, Target):
                assert ref not in targets
                targets[ref] = docstring.lines[0]

        return sections

    @classmethod
    def lines(cls, docstrings: Iterable[Docstring]) -> Iterator[str]:
        sections = cls._hierarchy(docstrings)

        is_first = True
        for section, subsections in sections.items():
            for subsection, targets in subsections.items():
                if not targets:
                    continue

                target_max_len = max(len(ref) for ref in targets)

                if is_first:
                    is_first = False
                else:
                    yield ""

                if subsection is None:
                    if section is not None:
                        yield f"{section}:"
                else:
                    yield f"{subsection}:"
                for target, summary in targets.items():
                    yield f" {target:>{target_max_len}}: {summary}"


def main() -> None:
    docstrings = Docstring.take_all(Stream(sys.stdin.readlines()))
    HelpFormatter.print(docstrings)


if __name__ == "__main__":
    main()
