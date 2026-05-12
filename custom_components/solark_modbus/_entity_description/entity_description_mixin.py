from typing import Any, Generic

from ..register_value_types import EntityDescriptionFactory, TEntityDescription, TSensorValue


class EntityDescriptionMixin(Generic[TEntityDescription, TSensorValue]):
    """Mixin for entities with entity descriptions."""

    _entity_description: TEntityDescription
    key: str
    name: str = ""
    entry_class: type[TEntityDescription]
    opts: dict[str, Any]

    ENTITY_DESCRIPTION_CLS: type[EntityDescriptionFactory[TEntityDescription]]

    # -----------------------------
    # Entity access
    # -----------------------------
    @property
    def entity_description(self) -> TEntityDescription:
        """Return the entity description for this entry."""
        return self._entity_description

    @entity_description.setter
    def entity_description(self, value: TEntityDescription) -> None:
        """Set the entity description for this entry."""
        self._entity_description = value

    def _create_entity_description(self, entry_class: type[TEntityDescription]) -> Any:
        """Subclasses must construct the entity description."""
        return self.ENTITY_DESCRIPTION_CLS.from_kwargs(
            key=self.key,
            name=self.name,
            entry_class=entry_class,
            opts=self.opts,
        )
