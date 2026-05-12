from typing import Any, Generic, Tuple

from ..register_value_types import TSensorValue
from .sensor_entity_description import SolArkSensorEntityDescription


class SensorMixin(Generic[TSensorValue]):
    """Mixin for sensor entities."""

    ENTITY_DESCRIPTION_CLS = SolArkSensorEntityDescription

    # Dynamic maps let entry classes convert raw values to custom display values and icons.
    DynamicValueAndIcon: dict[TSensorValue, Tuple[Any, str]] | None = None

    @classmethod
    def _get_dynamic_entry(
        cls, lookup_map_key: TSensorValue
    ) -> tuple[Any, str] | None:
        ''' Return the dictionary entry for the given key if DynamicValueAndIcon is configured. '''
        d = cls.DynamicValueAndIcon
        if not d:
            return None

        if lookup_map_key is None:
            raise ValueError(
                f"Value {lookup_map_key!r} is None. DynamicValueAndIcon keys: {list(d.keys())}"
            ) from None

        try:
            return d[lookup_map_key]
        except KeyError:
            raise ValueError(
                f"Value {lookup_map_key!r} not valid for DynamicValueAndIcon keys: {list(d.keys())}"
            ) from None

    @classmethod
    def dynamic_native_value(cls, lookup_map_key: TSensorValue) -> TSensorValue | None:
        """Return a dynamic display value if one is configured."""
        entry = cls._get_dynamic_entry(lookup_map_key)
        return entry[0] if entry else None

    @classmethod
    def dynamic_icon(cls, lookup_map_key: TSensorValue) -> str | None:
        """Return a dynamic icon for the value if one is configured."""
        entry = cls._get_dynamic_entry(lookup_map_key)
        return entry[1] if entry else None
