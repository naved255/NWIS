from pathlib import Path
from datetime import datetime
from ingestion import IngestionEngine, CSVDataSource, JSONDataSource
from ingestion.adapters import DatabaseDataSource, PDFMetadataAdapter

ROOT = Path(__file__).parents[1]


def test_csv_normalization_missing_and_duplicate():
    result = IngestionEngine().ingest(CSVDataSource(ROOT / "samples" / "wells.csv"), "well")
    assert result.total_records == 4
    assert result.accepted_count == 3
    assert result.duplicate_count == 1
    assert result.error_count == 0
    assert result.accepted[2].latitude is None
    assert result.accepted[2].longitude is None
    assert result.accepted[0].source_metadata.source_type == "csv"


def test_json_ingestion_and_duplicate_detection():
    result = IngestionEngine().ingest(JSONDataSource(ROOT / "samples" / "drilling_parameters.json"), "drilling_parameter")
    assert result.accepted_count == 2
    assert result.duplicate_count == 1
    assert result.accepted[0].well_id == "W-001"


def test_database_adapter():
    source = DatabaseDataSource(lambda: iter([{"well_id": "DB-1", "well_name": "Database Demo"}]))
    result = IngestionEngine().ingest(source, "well")
    assert result.accepted_count == 1
    assert result.accepted[0].well_id == "DB-1"
    assert result.accepted[0].source_metadata.source_type == "database"


def test_invalid_record_isolated():
    source = DatabaseDataSource(lambda: iter([{"well_id": "OK"}, {"well_id": ""}, {"well_id": "OK2"}]))
    result = IngestionEngine().ingest(source, "well")
    assert result.accepted_count == 2
    assert result.error_count == 1


def test_pdf_metadata_adapter(tmp_path):
    pdf = tmp_path / "completion_report.pdf"
    pdf.write_bytes(b"%PDF-demo")
    result = IngestionEngine().ingest(PDFMetadataAdapter(pdf), "document_metadata")
    assert result.accepted_count == 1
    assert result.accepted[0].mime_type == "application/pdf"
    assert result.accepted[0].extraction_status == "not_extracted"
