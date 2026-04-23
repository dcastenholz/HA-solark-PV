from dataclasses import replace
from typing import Iterable, TypeVar

from .base_map_entry import BaseMapEntry
from homeassistant.helpers.entity import EntityDescription


TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescription)
TEntry = TypeVar("TEntry", bound=BaseMapEntry)

class EntityDescriptionHelper():
    @staticmethod
    def set_entity_registry_enabled_default(entity_description: TEntityDescription, enabled: bool) -> TEntityDescription:
        return replace(entity_description, entity_registry_enabled_default = enabled)

    @staticmethod
    def set_map_entity_registry_enabled_default(base_map: Iterable[TEntry], enabled: bool):
        for entry in base_map:
            entry.entity_description = replace(entry.entity_description, entity_registry_enabled_default = enabled)
