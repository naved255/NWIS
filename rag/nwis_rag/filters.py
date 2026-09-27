"""Translate NWIS metadata filters into Qdrant filters."""

from __future__ import annotations

from qdrant_client.http import models as qmodels

from .schemas import RetrievalFilters


def build_qdrant_filter(filters: RetrievalFilters) -> qmodels.Filter | None:
    """Build an exact/range Qdrant payload filter from NWIS filters."""
    from qdrant_client.http import models as qmodels

    must: list[qmodels.FieldCondition] = []

    exact_fields = {
        "well_id": filters.well_id,
        "formation": filters.formation,
        "event_type": filters.event_type,
        "document_type": filters.document_type,
        "location": filters.location,
    }
    for field, value in exact_fields.items():
        if value is not None:
            must.append(qmodels.FieldCondition(key=field, match=qmodels.MatchValue(value=value)))

    if filters.depth_min is not None or filters.depth_max is not None:
        must.append(
            qmodels.FieldCondition(
                key="depth",
                range=qmodels.Range(gte=filters.depth_min, lte=filters.depth_max),
            )
        )

    if filters.date_from is not None or filters.date_to is not None:
        must.append(
            qmodels.FieldCondition(
                key="date",
                range=qmodels.DatetimeRange(
                    gte=(datetime.combine(filters.date_from, time.min) if filters.date_from else None),
                    lte=(datetime.combine(filters.date_to, time.max) if filters.date_to else None),
                ),
            )
        )

    return qmodels.Filter(must=must) if must else None
