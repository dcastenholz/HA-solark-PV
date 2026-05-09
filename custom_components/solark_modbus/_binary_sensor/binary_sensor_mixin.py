from .._binary_sensor.binary_sensor_entity_description import SolArkBinarySensorEntityDescription


class BinarySensorMixin:
    """Mixin for binary sensor entities."""

    ENTITY_DESCRIPTION_CLS = SolArkBinarySensorEntityDescription

    # Dynamic maps let entry classes override an icon for specific values.
    DynamicIcon: dict[bool, str] | None = None

    @classmethod
    def _get_dynamic_entry(
        cls, lookup_map_key: bool
    ) -> str | None:
        ''' Return the dictionary entry for the given key if DynamicIcon is configured. '''
        d = cls.DynamicIcon
        if not d:
            return None

        if lookup_map_key is None:
            raise ValueError(
                f"Value {lookup_map_key!r} is None. DynamicIcon keys: {list(d.keys())}"
            ) from None

        try:
            return d[lookup_map_key]
        except KeyError:
            raise ValueError(
                f"Value {lookup_map_key!r} not valid for DynamicIcon keys: {list(d.keys())}"
            ) from None

    @classmethod
    def dynamic_icon(cls, lookup_map_key: bool) -> str | None:
        """Return a dynamic icon for the value if one is configured."""
        entry = cls._get_dynamic_entry(lookup_map_key)
        return entry[0] if entry else None
