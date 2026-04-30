from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Self, Tuple

from .base_map_entry import BaseEntry
from .register_value_types import TBaseValue, TLookupMapKey, TMappedSensorValue, TRegisterValue, TSensorValue

if TYPE_CHECKING:
    from .data import SolArkData

class EntryLookup(Generic[TLookupMapKey, TBaseValue, TRegisterValue, TSensorValue], BaseEntry[Any, TBaseValue, TSensorValue], ABC):

    LOOKUP_MAP: dict[TLookupMapKey, Tuple[TSensorValue, str]]

    # mapped_sensor_value: TMappedSensorValue

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("dynamic_icon", self.dynamic_icon)
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls is EntryLookup:
            return  # don't validate base class itself

        # enforce override
        if "LOOKUP_MAP" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define LOOKUP_MAP")

        lookup = cls.LOOKUP_MAP
        if not isinstance(lookup, dict) or not lookup:
            raise TypeError(f"{cls.__name__}.LOOKUP_MAP must be a non-empty dict")

    @abstractmethod
    def dynamic_lookup_key(self, runtime_data: "SolArkData") -> TLookupMapKey:
        pass

    # TODO - This needs to be moved into BaseMap and rename this method with a separate call in the post processing pipeline.
    def _map_lookup(self: Self, runtime_data: "SolArkData") -> None:
        value: TLookupMapKey = self.dynamic_lookup_key(runtime_data)

        if value is None:
            return
            # raise TypeError("sensor_value is None")

        if value not in self.LOOKUP_MAP:
            raise TypeError(f"Value {value!r} not valid for LOOKUP_MAP keys: {list(self.LOOKUP_MAP.keys())}")

        self.sensor_value = self.LOOKUP_MAP[value][0]

    @classmethod
    def dynamic_icon(cls, value) -> str | None:
        if not isinstance(value, str):
            return None
        for _, (label, icon) in cls.LOOKUP_MAP.items():
            if label == value:
                return icon
        return None
