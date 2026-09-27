from types import SimpleNamespace

from geo.services.engine import GeoSpatialEngine
from geo.services.geojson import wells_to_feature_collection


def well(well_id, lat, lon, depth=3000, reservoir="R1"):
    return SimpleNamespace(
        id=well_id + "-db",
        well_id=well_id,
        well_name=well_id,
        field_name="Fictional Field",
        operator="SAMPLE",
        status="COMPLETED",
        latitude=lat,
        longitude=lon,
        total_depth_m=depth,
        metadata_json={"reservoir": reservoir},
    )


def formation(name="F1", reservoir="R1"):
    return SimpleNamespace(
        formation_name=name,
        properties={"reservoir": reservoir},
    )


class FakeRepo:
    def __init__(self):
        self.w1 = well("NWIS-DEMO-001", 27.5, 95.2)
        self.w2 = well("NWIS-DEMO-002", 27.53, 95.22, 3050)
        self._formations = {
            self.w1.well_id: [formation()],
            self.w2.well_id: [formation()],
        }

    def get_well(self, well_id):
        return {"NWIS-DEMO-001": self.w1, "NWIS-DEMO-002": self.w2}.get(well_id)

    def nearby(self, *args, **kwargs):
        if kwargs.get("exclude_well_id") == "NWIS-DEMO-001":
            return [(self.w2, 3.8)]
        return [(self.w1, 0.0), (self.w2, 3.8)]

    def formations(self, well_id):
        return self._formations.get(well_id, [])

    def events(self, well_id, limit=500):
        return [SimpleNamespace(event_type="FORMATION_ENTRY")]

    def parameters(self, well_id, depth_range=None, limit=5000):
        return [SimpleNamespace(
            weight_on_bit_kn=90, rotary_rpm=120, torque_kn_m=8,
            rate_of_penetration_m_hr=18, standpipe_pressure_kpa=12000,
            flow_rate_lpm=1800, mud_weight_kg_m3=1180,
        )]

    def trajectory(self, well_id):
        offset = 10 if well_id == "NWIS-DEMO-002" else 0
        return [
            SimpleNamespace(measured_depth_m=0, tvd_m=offset, inclination_deg=0, sequence_no=0),
            SimpleNamespace(measured_depth_m=1500, tvd_m=1490 + offset, inclination_deg=2.5, sequence_no=1),
        ]

    def trajectory_with_coordinates(self, well_id):
        return [
            (SimpleNamespace(measured_depth_m=0, tvd_m=0, inclination_deg=0, sequence_no=0), 95.2, 27.5),
            (SimpleNamespace(measured_depth_m=1500, tvd_m=1490, inclination_deg=2.5, sequence_no=1), 95.2, 27.5),
        ]


def test_nearby_returns_distance_and_metadata():
    result = GeoSpatialEngine(FakeRepo()).get_nearby_wells(27.5, 95.2, 10)
    assert result.count == 2
    assert result.wells[1].distance_km == 3.8
    assert "F1" in result.wells[0].formations


def test_similarity_is_bounded_and_explainable():
    result = GeoSpatialEngine(FakeRepo()).find_similar_offset_wells("NWIS-DEMO-001", 10)
    assert result.count == 1
    candidate = result.wells[0]
    assert 0 <= candidate.similarity_score <= 100
    assert candidate.factors.formation_score == 1.0
    assert candidate.shared_events == ["FORMATION_ENTRY"]


def test_geojson_is_leaflet_compatible():
    response = GeoSpatialEngine(FakeRepo()).get_nearby_wells(27.5, 95.2, 10)
    geojson = wells_to_feature_collection(response)
    assert geojson["type"] == "FeatureCollection"
    assert geojson["features"][0]["geometry"]["type"] == "Point"
    assert geojson["features"][0]["geometry"]["coordinates"] == [95.2, 27.5]


def test_trajectory_comparison():
    result = GeoSpatialEngine(FakeRepo()).compare_trajectories("NWIS-DEMO-001", "NWIS-DEMO-002")
    assert result.comparable_points == 2
    assert result.max_tvd_difference_m == 10
