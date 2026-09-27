from document_intelligence.models import Provenance, Page, StructuredDocument, DocumentMetadata


def test_document_contract_is_serializable():
    doc = StructuredDocument(
        document_id="DOC-1",
        file_name="sample.pdf",
        well_id="W-1",
        document_type="DDR",
        pages=[Page(page_number=1, text="hello", text_extraction_method="native", has_selectable_text=True,
                    provenance=Provenance(document_id="DOC-1", file_name="sample.pdf", page_number=1, source_type="DDR"))],
        metadata=DocumentMetadata(document_type="DDR", well_id="W-1", source_type="DDR"),
    )
    payload = doc.model_dump()
    assert payload["document_id"] == "DOC-1"
    assert payload["pages"][0]["provenance"]["document_id"] == "DOC-1"
