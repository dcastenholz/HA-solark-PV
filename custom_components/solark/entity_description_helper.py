"""Entity description helpers for SolArk."""

from dataclasses import replace
from typing import Iterable, TypeVar

from homeassistant.helpers.entity import EntityDescription

from .base_entry import BaseEntry

TEntityDescription = TypeVar("TEntityDescription", bound=EntityDescription)
TEntry = TypeVar("TEntry", bound=BaseEntry)

class EntityDescriptionHelper():
    """Helpers for updating entity description defaults."""

    @staticmethod
    def set_entity_registry_enabled_default(entity_description: TEntityDescription, enabled: bool) -> TEntityDescription:
        """Return an entity description with updated default enablement."""
        return replace(entity_description, entity_registry_enabled_default = enabled)

    @staticmethod
    def set_map_entity_registry_enabled_default(base_map: Iterable[TEntry], enabled: bool):
        """Set default enablement for all entries in a map."""
        for entry in base_map:
            entry.entity_description = replace(entry.entity_description, entity_registry_enabled_default = enabled)
