''' Class for defining and processing entries that are read from registers, or calculated from other entries or static data.'''
from abc import ABC

from .base_map_entry import BaseMapEntry

from .base_map import BaseMap


class SensorMap(BaseMap[BaseMapEntry], ABC):
    '''Sensor map may contain entries of any type that is a subclass of BaseMapEntry'''
    _entry_type = BaseMapEntry
