"""Leaflet-compatible GeoJSON serializers."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from ..models.schemas import GeoJSONFeatureCollection, GeoJSONFeature, NearbyWellsResponse


def wells_to_feature_collection(response: NearbyWellsResponse) -> dict[str, Any]:
    """Serialize nearby-well points to RFC 7946-style GeoJSON."""
    features = []
    for well in response.wells:
        properties = well.model_dump()
        properties.pop("latitude", None)
        properties.pop("longitude", None)
        features.append(
            GeoJSONFeature(
                geometry={"type": "Point", "coordinates": [well.longitude, well.latitude]},
                properties=properties,
            )
        )
    return GeoJSONFeatureCollection(
        features=features,
        metadata={
            "source": "NWIS geo-spatial intelligence module",
            "synthetic_data": False,
            "radius_km": response.radius_km,
        },
    ).model_dump()


def trajectories_to_feature_collection(rows: list[Any], well_id: str) -> dict[str, Any]:
    """Serialize stored trajectory points to a LineString where coordinates exist.

    Coordinates are read from the PostGIS geometry using ST_AsEWKT in the API
    adapter when available. This pure serializer accepts optional
    ``metadata_json.latitude/longitude`` as a dependency-free fallback.
    """
    coords = []
    for row, lon, lat in rows:
        if lon is not None and lat is not None:
            coords.append([float(lon), float(lat)])
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"well_id": well_id, "point_count": len(coords)},
        }],
        "metadata": {
            "source": "NWIS geo-spatial intelligence module",
            "synthetic_data": False,
        },
    }

def similar_offsets_to_feature_collection(response: Any) -> dict[str, Any]:
    """Serialize similarity-ranked wells to map-ready GeoJSON."""
    features = []
    for item in response.wells:
        well = item.well
        props = item.model_dump()
        props["well"] = None
        props.update({
            "well_id": well.well_id,
            "well_name": well.well_name,
            "distance_km": well.distance_km,
        })
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [well.longitude, well.latitude]},
            "properties": props,
        })
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "active_well_id": response.active_well_id,
            "radius_km": response.radius_km,
            "formation": response.formation,
            "synthetic_data": False,
        },
    }
