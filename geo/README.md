# NWIS Geo-Spatial Intelligence Module

This is a standalone **nearby/offset well intelligence** module for NWIS.
It consumes the existing NWIS SQLAlchemy/PostGIS models and does not create
duplicate database tables.

## Scope

Implemented:

- Radius search using PostGIS `ST_DWithin` and `ST_Distance`
- Distance from an active well
- Formation filtering
- Reservoir filtering
- Depth-range filtering
- Trajectory retrieval
- Trajectory comparison
- Explainable similar-offset ranking
- Leaflet-compatible GeoJSON
- Spatial-index deployment SQL
- Eight fictional demo wells
- Unit tests

Not implemented:

- React/Leaflet UI
- Risk prediction
- RAG/document retrieval
- Alerts/recommendations
- Real OIL data integration

The demo records are explicitly fictional and are **not real OIL India Limited data**.

## Architecture

```text
FastAPI router
     |
     v
GeoSpatialEngine
     |
     v
PostGISWellRepository
     |
     v
Existing NWIS database.models
     |
     v
PostgreSQL + PostGIS
```

The module uses the existing `wells.surface_location` GIST index and
`well_trajectories.point` GIST index. `sql/ensure_spatial_indexes.sql` is
provided as an idempotent deployment safeguard.

## Integration

From the NWIS project root, install the storage package first:

```bash
pip install -e nwis_db
pip install -r geo_spatial/requirements.txt
```

The storage package in the supplied project exposes:

```python
from database.db import get_session
from database.models import Well, WellTrajectory, Formation
```

Mount the router in the existing FastAPI application:

```python
from geo_spatial.api.router import router as geo_router

app.include_router(geo_router)
```

If the existing application uses a different API prefix, change the router
prefix in `geo_spatial/api/router.py` rather than changing the service.

## API

### Nearby wells

`GET /api/v1/geo/nearby`

Example:

```text
/api/v1/geo/nearby?latitude=27.5&longitude=95.2&radius_km=10
```

Optional filters:

```text
formation=Demo%20Sandstone
reservoir=Reservoir-A
depth_from_m=1800
depth_to_m=2400
limit=100
```

### Nearby GeoJSON

`GET /api/v1/geo/nearby/geojson`

Response:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [95.22, 27.53]
      },
      "properties": {
        "well_id": "NWIS-GEO-002",
        "distance_km": 3.8,
        "formations": ["Demo Sandstone"],
        "reservoirs": ["Reservoir-A"]
      }
    }
  ],
  "metadata": {
    "source": "NWIS geo-spatial intelligence module",
    "synthetic_data": false
  }
}
```

The coordinates follow GeoJSON order: `[longitude, latitude]`.

### Active well nearby search

`GET /api/v1/geo/wells/{active_well_id}/nearby`

Example:

```text
/api/v1/geo/wells/NWIS-GEO-001/nearby?radius_km=25
```

The response excludes the active well and includes PostGIS-calculated
`distance_km`.

### Similar offset wells

`GET /api/v1/geo/wells/{active_well_id}/offsets/similar`

Example:

```text
/api/v1/geo/wells/NWIS-GEO-001/offsets/similar?radius_km=25&formation=Demo%20Sandstone&depth_from_m=1800&depth_to_m=2400
```

Similarity is a deterministic, explainable heuristic:

| Factor | Weight |
|---|---:|
| Spatial distance | 30 |
| Formation | 20 |
| Reservoir | 10 |
| Depth overlap | 15 |
| Historical events | 15 |
| Drilling conditions | 10 |

Total = 100.

This is **not** an ML prediction. A later ML module can replace this ranking
behind the same response contract.

### Trajectory

`GET /api/v1/geo/wells/{well_id}/trajectory`

### Trajectory GeoJSON

`GET /api/v1/geo/wells/{well_id}/trajectory/geojson`

### Trajectory comparison

`GET /api/v1/geo/wells/{active_well_id}/trajectory-compare/{offset_well_id}`

Returns common depth interval, TVD differences, inclination differences, and
number of comparable points.

## Reservoir convention

The existing NWIS schema has no dedicated `reservoir` column. This module
therefore reads reservoir names from:

1. `wells.metadata["reservoir"]`
2. `formations.properties["reservoir"]`

This is an explicit adapter convention. If the final NWIS schema gains a
dedicated reservoir table/column, only `PostGISWellRepository` needs to be
updated.

## Depth convention

For well-level filtering, the existing schema provides `total_depth_m` but
not a single well-level start/end interval. The module treats a drilled well
as `[0, total_depth_m]` for coarse depth overlap.

Formation records retain the more precise formation intervals. The
`formation` filter therefore uses the actual `formations` table.

## Synthetic demo data

Run from the NWIS project root:

```bash
python geo_spatial/sample_data/seed_geo_demo.py
```

This creates eight wells in the fictional `Fictional North Field`.
Every inserted record carries `source=synthetic`.

Do not use these coordinates or records as OIL operational data.

## Tests

From the NWIS root:

```bash
pip install -r geo_spatial/requirements.txt
pytest geo_spatial/tests -q
```

The unit tests use an in-memory fake repository and do not require PostgreSQL.

## Environment variables

The module does not introduce database credentials of its own. It reuses the
existing NWIS storage configuration:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/nwis
```

The supplied storage package maps this through its `Settings.database_url`.
Use the project's existing environment configuration rather than adding
secrets to this module.

## Integration contract

The only required dependency is the existing storage-layer interface:

```python
PostGISWellRepository(session)
GeoSpatialEngine(repository)
```

The frontend does not need to know SQLAlchemy/PostGIS details. It consumes
the JSON or GeoJSON endpoints.

## Performance

The radius query uses:

```sql
ST_DWithin(
    geography(wells.surface_location),
    geography(ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)),
    :radius_m
)
```

and orders by `ST_Distance`. The spatial predicate can use the GIST index on
`surface_location`.

The trajectory geometry has its own GIST index. Additional well/depth indexes
are supplied in `sql/ensure_spatial_indexes.sql`.

For large production datasets, keep `limit` bounded and consider materialized
well-level reservoir/formation summaries rather than joining every historical
record for every map request.

## Known limitations

- Reservoir is currently metadata/property based because the supplied schema
  has no dedicated reservoir entity.
- Depth overlap at well level uses `[0, total_depth_m]`; formation intervals
  are more precise.
- Similarity is heuristic and should not be represented as an ML confidence.
- Drilling-condition similarity compares available mean parameter values.
- Trajectory comparison currently compares matching measured-depth samples;
  it does not interpolate between sparse samples.
- Authentication/authorization is intentionally left to the host NWIS API.
- No frontend code is included.
