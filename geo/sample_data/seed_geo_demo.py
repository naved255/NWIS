"""Insert fictional geo-spatial demo wells.

All records in this script are synthetic and must not be interpreted as OIL
India Limited data or field information.
"""
from decimal import Decimal
from datetime import datetime, timezone
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from database.db import SessionLocal
from database.models import Well, WellTrajectory, Formation, DrillingEvent, DrillingParameter


SYNTHETIC_NOTE = "FICTIONAL NWIS GEO DEMO DATA - NOT REAL OIL INDIA LIMITED DATA"


WELLS = [
    ("NWIS-GEO-001", "Fictional Alpha-01", 27.5000, 95.2000, 3200, "Reservoir-A"),
    ("NWIS-GEO-002", "Fictional Alpha-02", 27.5300, 95.2200, 3050, "Reservoir-A"),
    ("NWIS-GEO-003", "Fictional Alpha-03", 27.5550, 95.1850, 3300, "Reservoir-A"),
    ("NWIS-GEO-004", "Fictional Alpha-04", 27.6200, 95.2800, 3500, "Reservoir-B"),
    ("NWIS-GEO-005", "Fictional Alpha-05", 27.4550, 95.2700, 2900, "Reservoir-A"),
    ("NWIS-GEO-006", "Fictional Beta-01", 27.7200, 95.4000, 3600, "Reservoir-C"),
    ("NWIS-GEO-007", "Fictional Beta-02", 27.6700, 95.3400, 3450, "Reservoir-C"),
    ("NWIS-GEO-008", "Fictional Gamma-01", 27.4000, 95.1000, 2600, "Reservoir-B"),
]


def seed() -> None:
    """Insert eight synthetic wells and minimal geo-intelligence records."""
    with SessionLocal() as session:
        if session.scalar(select(Well).where(Well.well_id == "NWIS-GEO-001")):
            print("Geo demo data already present")
            return

        now = datetime.now(timezone.utc)
        wells = []
        for wid, name, lat, lon, depth, reservoir in WELLS:
            w = Well(
                well_id=wid,
                well_name=name,
                field_name="Fictional North Field",
                block_name="Demo Block",
                operator="SAMPLE",
                status="COMPLETED",
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lon)),
                total_depth_m=Decimal(str(depth)),
                surface_location=WKTElement(f"POINT({lon} {lat})", srid=4326),
                metadata_json={"source": "synthetic", "note": SYNTHETIC_NOTE, "reservoir": reservoir},
            )
            session.add(w)
            wells.append((w, reservoir))
        session.flush()

        for w, reservoir in wells:
            session.add(
                Formation(
                    well_id=w.id,
                    formation_name="Demo Sandstone",
                    top_depth_m=Decimal("1800"),
                    base_depth_m=Decimal("2400"),
                    lithology="sandstone",
                    properties={"reservoir": reservoir, "source": "synthetic"},
                )
            )
            for seq, md, tvd, inc in [
                (0, 0, 0, 0),
                (1, 1500, 1490, 2.5),
                (2, 2400, 2375, 4.0),
            ]:
                session.add(
                    WellTrajectory(
                        well_id=w.id,
                        measured_depth_m=Decimal(str(md)),
                        tvd_m=Decimal(str(tvd)),
                        inclination_deg=Decimal(str(inc)),
                        azimuth_deg=Decimal("90"),
                        sequence_no=seq,
                        point=WKTElement(
                            f"POINT Z({w.longitude} {w.latitude} {tvd})", srid=4326
                        ),
                        metadata_json={"source": "synthetic"},
                    )
                )
            session.add(
                DrillingEvent(
                    well_id=w.id,
                    event_type="FORMATION_ENTRY",
                    event_time=now,
                    depth_m=Decimal("1800"),
                    severity="INFO",
                    description="Synthetic formation entry",
                    metadata_json={"source": "synthetic", "note": SYNTHETIC_NOTE},
                )
            )
            session.add(
                DrillingParameter(
                    well_id=w.id,
                    recorded_at=now,
                    measured_depth_m=Decimal("2000"),
                    weight_on_bit_kn=Decimal("90"),
                    rotary_rpm=Decimal("120"),
                    torque_kn_m=Decimal("8"),
                    rate_of_penetration_m_hr=Decimal("18"),
                    standpipe_pressure_kpa=Decimal("12000"),
                    flow_rate_lpm=Decimal("1800"),
                    mud_weight_kg_m3=Decimal("1180"),
                    metadata_json={"source": "synthetic"},
                )
            )

        session.commit()
        print(f"Inserted {len(wells)} fictional geo demo wells")


if __name__ == "__main__":
    seed()
