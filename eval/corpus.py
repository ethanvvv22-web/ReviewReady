"""A labeled corpus of representative contributions.

Each sample carries ground-truth `expected` categories (what a reviewer would
legitimately flag). Clean samples expect an empty set, so false positives are
measurable. This stands in for 'representative validation-framework
contributions' until a real one is available.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Sample:
    name: str
    source: str
    has_tests: bool
    expected: set


CLEAN = '''"""A clean utility module."""


def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b
'''

CLEAN_DRIVER = '''"""Temperature driver."""
import logging

logger = logging.getLogger(__name__)


class TemperatureDriver:
    """Temperature sensor driver."""

    def open(self) -> None:
        """Open."""
        logger.info("open")

    def read(self) -> float:
        """Read."""
        return 1.0

    def close(self) -> None:
        """Close."""
        logger.info("close")
'''

NO_DOCSTRING = '''import logging


def compute(x: int) -> int:
    return x * 2
'''

UNTYPED = '''"""Module."""


def compute(x, y):
    """Compute something."""
    return x + y
'''

BARE_PRINT = '''"""Module."""


def run() -> None:
    """Run it."""
    try:
        print("working")
    except:
        pass
'''

MUTABLE = '''"""Module."""


def collect(items: list = []) -> list:
    """Collect items."""
    return items
'''

BAD_NAMES = '''"""Module."""


def DoThing() -> int:
    """Do a thing."""
    return 1


class myHandler:
    """A handler."""
'''

UNUSED_STAR = '''"""Module."""
import os
import json
from math import *


def ping() -> int:
    """Ping."""
    return 1
'''

BAD_DEP = '''"""Module."""
import tensorflow


def model() -> object:
    """Build a model."""
    return tensorflow.keras.Model()
'''

DRIVER_IFACE = '''"""Module."""


class SensorDriver:
    """A sensor driver."""

    def read(self) -> int:
        """Read value."""
        return 1
'''

NO_TESTS = '''"""A clean module that simply lacks tests."""


def square(n: int) -> int:
    """Return n squared."""
    return n * n
'''

TODO_LONG = '''"""Module."""


def helper() -> int:
    """Helper."""
    x = 1  # TODO: replace this placeholder with the real computation and input-validation logic in a later iteration of this driver
    return x
'''


def build_corpus() -> list[Sample]:
    return [
        Sample("clean_util", CLEAN, True, set()),
        Sample("clean_driver", CLEAN_DRIVER, True, set()),
        Sample("no_docstring", NO_DOCSTRING, True,
               {"missing-module-docstring", "missing-func-docstring", "unused-import"}),
        Sample("untyped", UNTYPED, True, {"missing-type-hints"}),
        Sample("bare_print", BARE_PRINT, True, {"bare-except", "print-statement"}),
        Sample("mutable_default", MUTABLE, True, {"mutable-default"}),
        Sample("bad_names", BAD_NAMES, True, {"naming-convention"}),
        Sample("unused_star", UNUSED_STAR, True, {"unused-import", "star-import"}),
        Sample("bad_dep", BAD_DEP, True, {"non-approved-dependency"}),
        Sample("driver_iface", DRIVER_IFACE, True, {"interface-missing-method"}),
        Sample("no_tests", NO_TESTS, False, {"missing-tests"}),
        Sample("todo_long", TODO_LONG, True, {"todo-left", "line-too-long"}),
    ]
