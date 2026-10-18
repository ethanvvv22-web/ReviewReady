"""Temperature sensor driver for the validation framework."""
import logging

logger = logging.getLogger(__name__)


class TemperatureDriver:
    """Driver for the temperature sensor."""

    def open(self) -> None:
        """Open the connection to the sensor."""
        logger.info("opening connection")

    def read(self) -> float:
        """Return the current temperature in Celsius."""
        return 21.5

    def close(self) -> None:
        """Close the connection to the sensor."""
        logger.info("closing connection")
