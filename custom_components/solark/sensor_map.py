from typing import TYPE_CHECKING

from .base_map import BaseMap
from .sensor_map_entry import SensorMapEntry


class SensorMap(BaseMap[SensorMapEntry]):
    _entry_type = SensorMapEntry
