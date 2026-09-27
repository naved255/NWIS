"""PostGIS data-access adapter for geo-spatial intelligence."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session

def _models():
    """Import shared NWIS ORM models lazily so pure unit tests need no DB package."""
    from database.models import DrillingEvent, DrillingParameter, Formation, Well, WellTrajectory
    return DrillingEvent, DrillingParameter, Formation, Well, WellTrajectory



class PostGISWellRepository:
    """Read-only adapter over the existing NWIS storage models.

    The repository deliberately imports the shared ``database`` package rather
    than defining duplicate ORM models. It therefore remains compatible with
    the existing NWIS schema.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_well(self, well_id: str):
        _, _, _, Well, _ = _models()
        return self.session.scalar(select(Well).where(Well.well_id == well_id))

    def nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        formation: str | None = None,
        reservoir: str | None = None,
        depth_range: tuple[float, float] | None = None,
        exclude_well_id: str | None = None,
        limit: int = 100,
    ) -> list[tuple[Any, float]]:
        """Find wells with an indexed PostGIS geography distance predicate."""
        _, _, Formation, Well, _ = _models()
        if radius_km <= 0:
            raise ValueError("radius_km must be greater than zero")
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        origin = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
        geography_origin = func.Geography(origin)
        geography_well = func.Geography(Well.surface_location)
        distance_km = func.ST_Distance(geography_well, geography_origin) / 1000.0

        stmt = (
            select(Well, distance_km.label("distance_km"))
            .where(
                func.ST_DWithin(
                    geography_well,
                    geography_origin,
                    radius_km * 1000.0,
                )
            )
            .order_by(distance_km)
            .limit(limit)
        )

        if exclude_well_id:
            stmt = stmt.where(Well.well_id != exclude_well_id)

        if formation:
            formation_exists = select(Formation.id).where(
                Formation.well_id == Well.id,
                func.lower(Formation.formation_name) == formation.strip().lower(),
            ).exists()
            stmt = stmt.where(formation_exists)

        if reservoir:
            reservoir_value = reservoir.strip().lower()
            well_reservoir = Well.metadata_json["reservoir"].as_string()
            formation_reservoir = Formation.properties["reservoir"].as_string()
            reservoir_exists = select(Formation.id).where(
                Formation.well_id == Well.id,
                func.lower(formation_reservoir) == reservoir_value,
            ).exists()
            stmt = stmt.where(
                or_(
                    func.lower(well_reservoir) == reservoir_value,
                    reservoir_exists,
                )
            )

        if depth_range:
            start, end = sorted(depth_range)
            # A well is a coarse depth-overlap match when its drilled interval
            # [0, total_depth] intersects the requested interval.
            stmt = stmt.where(
                Well.total_depth_m.is_not(None),
                Well.total_depth_m >= start,
            )

        return [(well, float(distance)) for well, distance in self.session.execute(stmt).all()]

    def formations(self, well_id: str) -> list[Any]:
        _, _, Formation, _, _ = _models()
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = select(Formation).where(Formation.well_id == well.id).order_by(Formation.top_depth_m)
        return list(self.session.scalars(stmt).all())

    def events(self, well_id: str, limit: int = 500) -> list[Any]:
        _, DrillingEvent, _, _, _ = _models()
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = (
            select(DrillingEvent)
            .where(DrillingEvent.well_id == well.id)
            .order_by(DrillingEvent.event_time)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def parameters(
        self,
        well_id: str,
        depth_range: tuple[float, float] | None = None,
        limit: int = 5000,
    ) -> list[Any]:
        _, DrillingParameter, _, _, _ = _models()
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = select(DrillingParameter).where(DrillingParameter.well_id == well.id)
        if depth_range:
            start, end = sorted(depth_range)
            stmt = stmt.where(
                DrillingParameter.measured_depth_m >= start,
                DrillingParameter.measured_depth_m <= end,
            )
        stmt = stmt.order_by(DrillingParameter.measured_depth_m).limit(limit)
        return list(self.session.scalars(stmt).all())

    def trajectory(self, well_id: str) -> list[Any]:
        _, _, _, _, WellTrajectory = _models()
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = (
            select(WellTrajectory)
            .where(WellTrajectory.well_id == well.id)
            .order_by(WellTrajectory.sequence_no)
        )
        return list(self.session.scalars(stmt).all())

    def trajectory_with_coordinates(self, well_id: str) -> list[tuple[Any, float | None, float | None]]:
        """Return trajectory rows plus longitude/latitude extracted by PostGIS."""
        _, _, _, _, WellTrajectory = _models()
        well = self.get_well(well_id)
        if well is None:
            return []
        stmt = (
            select(
                WellTrajectory,
                func.ST_X(func.ST_Force2D(WellTrajectory.point)).label("longitude"),
                func.ST_Y(func.ST_Force2D(WellTrajectory.point)).label("latitude"),
            )
            .where(WellTrajectory.well_id == well.id)
            .order_by(WellTrajectory.sequence_no)
        )
        return [
            (row[0], float(row.longitude) if row.longitude is not None else None,
             float(row.latitude) if row.latitude is not None else None)
            for row in self.session.execute(stmt).all()
        ]

    def spatial_indexes_sql(self) -> str:
        """Return idempotent SQL that guarantees the required spatial indexes."""
        return """
CREATE INDEX IF NOT EXISTS ix_wells_surface_location_gist
    ON wells USING GIST (surface_location);
CREATE INDEX IF NOT EXISTS ix_well_trajectories_point_gist
    ON well_trajectories USING GIST (point);
""".strip()

