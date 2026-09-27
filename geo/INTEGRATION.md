# Integration Checklist

1. Copy `geo_spatial/` into the NWIS project root.
2. Install the existing storage package:
   `pip install -e nwis_db`
3. Install:
   `pip install -r geo_spatial/requirements.txt`
4. Ensure PostgreSQL has PostGIS enabled.
5. Run `geo_spatial/sql/ensure_spatial_indexes.sql`.
6. Mount `geo_spatial.api.router.router` into the existing FastAPI app.
7. Configure the existing `DATABASE_URL`.
8. Optionally run `python geo_spatial/sample_data/seed_geo_demo.py`.
9. Run `pytest geo_spatial/tests -q`.

No existing NWIS source file needs to be modified to use the service itself.
The only host-application change required is registering the router.
