"""Coordinator data set for caching."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from ..register_value_types import SensorValue


@dataclass
class CoordinatorData:
    """Coordinator data set and the time it was processed."""

    data: dict[str, SensorValue]
    timestamp: datetime

    @property
    def age(self) -> timedelta:
        """Return the age of this data set."""
        return datetime.now() - self.timestamp
