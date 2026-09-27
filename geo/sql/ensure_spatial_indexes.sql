-- NWIS geo-spatial module: idempotent PostGIS indexes.
-- Run after PostGIS is enabled. Existing NWIS ORM models already request
-- spatial indexes; these statements are a deployment-safe verification path.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE INDEX IF NOT EXISTS ix_wells_surface_location_gist
    ON wells USING GIST (surface_location);

CREATE INDEX IF NOT EXISTS ix_well_trajectories_point_gist
    ON well_trajectories USING GIST (point);

CREATE INDEX IF NOT EXISTS ix_well_trajectories_well_depth
    ON well_trajectories (well_id, measured_depth_m);

CREATE INDEX IF NOT EXISTS ix_formations_well_depth
    ON formations (well_id, top_depth_m, base_depth_m);
