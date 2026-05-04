''' Class for defining and processing entries that are read from registers, or calculated from other entries or static data.'''
from abc import ABC

from .base_entry import BaseEntry
from .base_map import BaseMap
from .sensor_entry import BaseSensorEntry


class SensorMap(BaseMap[BaseSensorEntry], ABC):
    '''Sensor map may contain entries of any type that is a subclass of BaseEntry'''
    _entry_type = BaseEntry
