from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .register_value_types import RegisterValue


@dataclass
class CoordinatorData:
    data: dict[str, RegisterValue]
    timestamp: datetime

    @property
    def age(self) -> timedelta:
        return datetime.now() - self.timestamp
