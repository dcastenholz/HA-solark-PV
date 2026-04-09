import logging
from abc import ABC
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Iterator, Type, TypeVar, cast

from homeassistant.const import EntityCategory

from .base_map_entry import BaseMapEntry
from .register_value_types import RegisterValue
from .sensor_entity_description import SolArkModbusSensorEntityDescription

_LOGGER = logging.getLogger(__name__)

TEntry = TypeVar("TEntry", bound=BaseMapEntry)

if TYPE_CHECKING:
    from .data import SolArkData


class BaseMap(Generic[TEntry], ABC):
    """Generic base class for entry-based maps using class attribute collection."""
    _entry_type: ClassVar[type[Any]]
    _class_entries: ClassVar[list[Any]]
    _entries: list[TEntry]
    runtime_data: "SolArkData"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        entry_type = getattr(cls, "_entry_type", None)
        if not isinstance(entry_type, type):
            raise TypeError(f"{cls.__name__} must define _entry_type")

        cls._class_entries = cls._collect_entries(cls.__mro__, entry_type)

    # ----------------------------------
    # Post process methods
    # ----------------------------------
    def post_process(self):
        """Post-process the register map entries after reading the raw values from the inverter."""
        # TODO - Handle case where the dependency registers were not read. Value is None
        for entry in self:
            if entry.post_process is not None:
                entry.do_post_process(self.runtime_data)

    @staticmethod
    def _collect_entries(mro: tuple[type, ...], entry_cls: Type[Any]) -> list[TEntry]:
        entries: list[TEntry] = []

        # Collect all map entry attributes from the class and parent classes
        # Walk full inheritance chain
        for base in reversed(mro):
            for value in base.__dict__.values():
                if isinstance(value, entry_cls):
                    entries.append(cast(TEntry, value))

        return entries

    def __init__(self, runtime_data: "SolArkData"):
        self.runtime_data = runtime_data

        self._entries: list[TEntry] = cast(
            list[TEntry],
            list(self.__class__._class_entries),
        )

        self._error = False

        self._sort()
        self._validate()

    # ---- override points ----
    def _sort(self):
        pass

    def _validate(self):
        pass

    # ---- shared API ----
    def __iter__(self) -> Iterator[TEntry]:
        return iter(self._entries)

    def get_descriptions(self) -> list[SolArkModbusSensorEntityDescription]:
        return [
            entry.entity_description
            for entry in self._entries
            # Modern HA does not allow use EntityCategory.CONFIG for sensors.
            if entry.entity_description.entity_category != EntityCategory.CONFIG
        ]

    def as_dict(self) -> dict[str, RegisterValue]:
        return {
            entry.entity_description.key: entry.register_value
            for entry in self._entries
        }
