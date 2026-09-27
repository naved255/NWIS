from fastapi import APIRouter, Depends, Query
from ..dependencies import get_knowledge_service
from ..schemas import *
from ..services.interfaces import KnowledgeService

router = APIRouter(tags=["Knowledge"])

@router.get("/documents", response_model=DocumentListResponse, summary="List drilling documents")
def documents(well_id: str | None = None, document_type: str | None = None, limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), service: KnowledgeService = Depends(get_knowledge_service)):
    items, total = service.documents(well_id, document_type, limit, offset)
    return DocumentListResponse(items=items, pagination=Pagination(limit=limit, offset=offset, total=total))

@router.post("/search", response_model=SearchResponse, summary="Search historical knowledge")
def search(request: SearchRequest, service: KnowledgeService = Depends(get_knowledge_service)):
    filters = request.model_dump(exclude={"query", "limit"}, exclude_none=True)
    return SearchResponse(query=request.query, items=service.search(request.query, filters, request.limit))

@router.post("/rag", response_model=RAGResponse, summary="Ask the historical drilling knowledge service")
def rag(request: RAGRequest, service: KnowledgeService = Depends(get_knowledge_service)):
    filters = request.model_dump(exclude={"query", "limit", "include_sources"}, exclude_none=True)
    answer, sources = service.answer(request.query, filters, request.include_sources)
    return RAGResponse(question=request.query, answer=answer, sources=sources)
