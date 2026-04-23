from abc import ABC
from typing import ClassVar, Dict, Generic, Tuple, TypeVar, cast

from .base_map_entry import BaseMapEntry
from .register_value_types import SensorValue

T = TypeVar("T", bound="MapEntryLookup")
TSensorValue = TypeVar("TSensorValue", bound=SensorValue)

# class MapEntryLookup(Generic[TSensorValue], ABC):
    # # Override in subclasses
    # LOOKUP_MAP: Dict[TSensorValue, Tuple[str, str]]
class MapEntryLookup(ABC):
    # Override in subclasses
    # TODO - The key should be a generic type
    LOOKUP_MAP: Dict[int, Tuple[str, str]]

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("dynamic_icon", self.dynamic_icon)
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls is MapEntryLookup:
            return  # don't validate base class itself

        # enforce override
        if "LOOKUP_MAP" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define LOOKUP_MAP")

        lookup = cls.LOOKUP_MAP
        if not isinstance(lookup, dict) or not lookup:
            raise TypeError(f"{cls.__name__}.LOOKUP_MAP must be a non-empty dict")

    # @classmethod
    # def lookup_icon_from_map(cls, state: str) -> str | None:
    #     for _, (label, icon) in cls.LOOKUP_MAP.items():
    #         if label == state:
    #             return icon
    #     return None

    def set_mapped_sensor_value(self, entry: BaseMapEntry) -> None:
        # TODO - The key should be a generic type
        if not isinstance(self , BaseMapEntry):
            raise ValueError("MapEntryLookup can only be applied to BaseMapEntry subclasses")
        entry = cast(BaseMapEntry, self)
        if not isinstance(entry.sensor_value , int):
            raise NotImplementedError("Only int is allowed for key value in LOOKUP_MAP")
        entry.sensor_value = self.LOOKUP_MAP[entry.sensor_value][0]

    @classmethod
    def get_label_from_raw(self, raw: int) -> str:
        return self.LOOKUP_MAP[raw][0]

    @classmethod
    def dynamic_icon(cls, value) -> str | None:
        if not isinstance(value, str):
            return None
        for _, (label, icon) in cls.LOOKUP_MAP.items():
            if label == value:
                return icon
        return None
