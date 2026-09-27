from pathlib import Path
from database.schemas import WellCreate, QdrantChunkPayload
from database.storage import LocalObjectStorage


def test_well_schema_validates_coordinates():
    well = WellCreate(well_id="W1", latitude=27.5, longitude=95.2)
    assert well.well_id == "W1"
    assert float(well.latitude) == 27.5


def test_qdrant_payload_contains_required_metadata():
    payload = QdrantChunkPayload(chunk_id="c1", document_id="d1", well_id="W1", formation="F1", depth=1200, document_type="DDR", event_type="KICK", text="sample")
    assert payload.well_id == "W1"
    assert payload.document_type == "DDR"


def test_local_object_storage_roundtrip(tmp_path: Path):
    store = LocalObjectStorage(tmp_path)
    store.put("wells/a.pdf", b"abc", "application/pdf")
    assert store.exists("wells/a.pdf")
    assert store.get("wells/a.pdf") == b"abc"
    store.delete("wells/a.pdf")
    assert not store.exists("wells/a.pdf")


def test_local_object_storage_blocks_path_escape(tmp_path: Path):
    store = LocalObjectStorage(tmp_path)
    try:
        store.put("../escape.txt", b"no")
        assert False, "path traversal should fail"
    except ValueError:
        pass
