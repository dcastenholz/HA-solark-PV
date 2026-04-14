
from .base_map_entry import BaseMapEntry

from .base_map import BaseMap


class SensorMap(BaseMap[BaseMapEntry]):
    _entry_type = BaseMapEntry
