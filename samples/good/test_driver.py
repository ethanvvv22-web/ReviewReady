"""Tests for the temperature driver."""
from driver import TemperatureDriver


def test_read():
    assert TemperatureDriver().read() == 21.5
