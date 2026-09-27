"""Read-oriented repository interfaces for NWIS well intelligence."""
from __future__ import annotations
from collections.abc import Sequence
from sqlalchemy import select, text, func
from sqlalchemy.orm import Session
from ..models import Well, DrillingEvent, DrillingParameter, Formation, GeologicalInformation
from ..schemas import SimilarWellMetadata


class WellRepository:
    """Encapsulates persistent retrieval operations used by other NWIS modules."""

    def __init__(self, session: Session):
        self.session = session

    def get_well(self, well_id: str) -> Well | None:
        """Return a well by its external well identifier."""
        return self.session.scalar(select(Well).where(Well.well_id == well_id))

    def get_nearby_wells(self, well_id: str, radius_km: float, limit: int = 50) -> Sequence[Well]:
        """Return wells within ``radius_km`` of a source well, excluding itself."""
        if radius_km < 0:
            raise ValueError("radius_km must be non-negative")
        source = self.get_well(well_id)
        if source is None:
            return []
        # ST_DWithin geography uses metres and avoids degree-based distance errors.
        distance = func.ST_Distance(
            func.Geography(Well.surface_location),
            func.Geography(source.surface_location),
        )
        stmt = (
            select(Well)
            .where(Well.id != source.id)
            .where(func.ST_DWithin(func.Geography(Well.surface_location), func.Geography(source.surface_location), radius_km * 1000.0))
            .order_by(distance)
            .limit(limit)
        )
        return self.session.scalars(stmt).all()

    def get_well_events(self, well_id: str, event_type: str | None = None, limit: int = 500) -> Sequence[DrillingEvent]:
        """Return drilling events ordered chronologically for a well."""
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = select(DrillingEvent).where(DrillingEvent.well_id == well.id).order_by(DrillingEvent.event_time).limit(limit)
        if event_type:
            stmt = stmt.where(DrillingEvent.event_type == event_type)
        return self.session.scalars(stmt).all()

    def get_drilling_parameters(self, well_id: str, depth_from_m: float | None = None, depth_to_m: float | None = None, limit: int = 5000) -> Sequence[DrillingParameter]:
        """Return drilling parameter records optionally constrained by measured depth."""
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = select(DrillingParameter).where(DrillingParameter.well_id == well.id).order_by(DrillingParameter.recorded_at).limit(limit)
        if depth_from_m is not None:
            stmt = stmt.where(DrillingParameter.measured_depth_m >= depth_from_m)
        if depth_to_m is not None:
            stmt = stmt.where(DrillingParameter.measured_depth_m <= depth_to_m)
        return self.session.scalars(stmt).all()

    def get_formation_data(self, well_id: str, depth_m: float | None = None) -> Sequence[Formation]:
        """Return formations intersecting an optional measured depth."""
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = select(Formation).where(Formation.well_id == well.id).order_by(Formation.top_depth_m)
        if depth_m is not None:
            stmt = stmt.where(Formation.top_depth_m <= depth_m, Formation.base_depth_m >= depth_m)
        return self.session.scalars(stmt).all()

    def get_similar_wells_metadata(self, well_id: str, radius_km: float = 25.0, limit: int = 20) -> list[SimilarWellMetadata]:
        """Return spatially nearby wells with distance, shared formations and event types.

        This is metadata retrieval only; it does not perform ML similarity ranking.
        """
        source = self.get_well(well_id)
        if source is None:
            return []
        dist_expr = func.ST_Distance(func.Geography(Well.surface_location), func.Geography(source.surface_location)) / 1000.0
        stmt = (
            select(Well, dist_expr.label("distance_km"))
            .where(Well.id != source.id)
            .where(func.ST_DWithin(func.Geography(Well.surface_location), func.Geography(source.surface_location), radius_km * 1000.0))
            .order_by(dist_expr)
            .limit(limit)
        )
        rows = self.session.execute(stmt).all()
        source_formations = set(self.session.scalars(select(Formation.formation_name).where(Formation.well_id == source.id)).all())
        results: list[SimilarWellMetadata] = []
        for well, distance_km in rows:
            formations = set(self.session.scalars(select(Formation.formation_name).where(Formation.well_id == well.id)).all())
            events = set(self.session.scalars(select(DrillingEvent.event_type).where(DrillingEvent.well_id == well.id)).all())
            results.append(SimilarWellMetadata.model_validate({
                "id": well.id, "well_id": well.well_id, "well_name": well.well_name,
                "field_name": well.field_name, "block_name": well.block_name,
                "operator": well.operator, "status": well.status,
                "latitude": well.latitude, "longitude": well.longitude,
                "total_depth_m": well.total_depth_m, "metadata": well.metadata_json,
                "distance_km": float(distance_km),
                "formation_matches": sorted(source_formations & formations),
                "event_types": sorted(events),
            }))
        return results

    def get_geological_information(self, well_id: str, depth_from_m: float | None = None, depth_to_m: float | None = None) -> Sequence[GeologicalInformation]:
        """Return geological intervals for a well."""
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = select(GeologicalInformation).where(GeologicalInformation.well_id == well.id).order_by(GeologicalInformation.depth_from_m)
        if depth_from_m is not None:
            stmt = stmt.where(GeologicalInformation.depth_to_m >= depth_from_m)
        if depth_to_m is not None:
            stmt = stmt.where(GeologicalInformation.depth_from_m <= depth_to_m)
        return self.session.scalars(stmt).all()
