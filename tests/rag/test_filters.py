import pytest

pytest.importorskip("qdrant_client")

from datetime import date

from nwis_rag.filters import build_qdrant_filter
from nwis_rag.schemas import RetrievalFilters


def test_builds_metadata_filter():
    result = build_qdrant_filter(
        RetrievalFilters(
            well_id="W-1",
            formation="F-1",
            depth_min=2800,
            depth_max=3000,
            event_type="mud_loss",
            document_type="DDR",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            location="FIELD-A",
        )
    )
    assert result is not None
    assert len(result.must) == 7
