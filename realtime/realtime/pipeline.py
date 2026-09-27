from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from .models import DrillingParameterUpdate, NormalizedRealtimeEvent, ValidationIssue
from .normalizer import normalize_update
from .validator import ParameterLimits, validate_update

logger = logging.getLogger(__name__)
PredictionCallback = Callable[[DrillingParameterUpdate], Awaitable[object | None]]


class RealtimePipeline:
    """Validate, normalize, classify and forward real-time drilling samples."""

    def __init__(self, prediction_callback: PredictionCallback | None = None, limits: ParameterLimits | None = None) -> None:
        self.prediction_callback = prediction_callback
        self.limits = limits

    async def process(self, payload: DrillingParameterUpdate | dict, well_id: str | None = None) -> NormalizedRealtimeEvent:
        """Process one provider payload and optionally send it to prediction."""
        update = payload if isinstance(payload, DrillingParameterUpdate) else normalize_update(payload, well_id=well_id)
        issues = validate_update(update, self.limits) if self.limits is not None else validate_update(update)
        abnormal = [issue.field for issue in issues]

        event = NormalizedRealtimeEvent(
            event_type="abnormal_parameter" if abnormal else "parameter_update",
            well_id=update.well_id,
            timestamp=update.timestamp,
            parameters=update,
            abnormal_fields=abnormal,
            issues=issues,
            source=update.source,
        )

        if self.prediction_callback is not None:
            try:
                await self.prediction_callback(update)
            except Exception:
                # Real-time delivery must not die because a downstream
                # prediction service is temporarily unavailable.
                logger.exception("Prediction callback failed well_id=%s sequence=%s", update.well_id, update.sequence)
        return event
