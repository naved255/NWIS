"""Pydantic-backed entity validation."""
from __future__ import annotations
from pydantic import ValidationError
from ..models import ENTITY_MODELS, NWISEntity


class EntityValidator:
    """Validate normalized dictionaries against canonical Pydantic models."""

    def validate(self, entity_type: str, record: dict) -> NWISEntity:
        """Return a validated entity or raise ``ValidationError``."""
        try:
            model = ENTITY_MODELS[entity_type]
        except KeyError as exc:
            raise ValueError(f"Unsupported entity type: {entity_type}") from exc
        return model.model_validate(record)
