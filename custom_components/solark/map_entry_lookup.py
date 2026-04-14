from abc import ABC
from typing import ClassVar, Dict, Tuple, TypeVar

T = TypeVar("T", bound="MapEntryLookup")


class MapEntryLookup(ABC):
    # Override in subclasses
    LOOKUP_MAP: ClassVar[Dict[int, Tuple[str, str]]]

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

    @classmethod
    def lookup_icon_from_map(cls, state: str) -> str | None:
        for _, (label, icon) in cls.LOOKUP_MAP.items():
            if label == state:
                return icon
        return None

    @classmethod
    def get_label_from_raw(cls, raw: int) -> str:
        return cls.LOOKUP_MAP[raw][0]

    @classmethod
    def dynamic_icon(cls, value) -> str | None:
        if not isinstance(value, str):
            return None
        return cls.lookup_icon_from_map(value)
