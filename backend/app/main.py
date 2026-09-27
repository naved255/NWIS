from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .errors import ResourceNotFound, ServiceUnavailable, ValidationServiceError
from .logging_config import configure_logging
from .schemas import HealthResponse
from .routers import wells, knowledge, predictions, operations, realtime

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("nwis.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s version=%s mode=%s", settings.app_name, settings.api_version, settings.service_mode)
    yield
    logger.info("Stopping %s", settings.app_name)

app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="Stable REST/WebSocket API gateway for the AI-Powered Nearby Wells Intelligence System (NWIS).",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for prefix in (f"/api/{settings.api_version}", "/api"):
    app.include_router(wells.router, prefix=prefix)
    app.include_router(knowledge.router, prefix=prefix)
    app.include_router(predictions.router, prefix=prefix)
    app.include_router(operations.router, prefix=prefix)
    app.include_router(realtime.router, prefix=prefix)

@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"], summary="Service health")
@app.get("/api/health", response_model=HealthResponse, tags=["System"], include_in_schema=False)
def health():
    dependencies = {"api": "ok", "database": "configured" if settings.enable_database else "mock", "knowledge": "mock", "ml": "mock", "realtime": "mock"}
    status = "ok" if settings.environment == "development" or not settings.enable_database else "degraded"
    return HealthResponse(status=status, service=settings.app_name, version=settings.api_version, dependencies=dependencies)

@app.exception_handler(ResourceNotFound)
async def not_found_handler(_: Request, exc: ResourceNotFound):
    return JSONResponse(status_code=404, content={"error": {"code": "NOT_FOUND", "message": str(exc)}})

@app.exception_handler(ValidationServiceError)
async def validation_handler(_: Request, exc: ValidationServiceError):
    return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "message": str(exc)}})

@app.exception_handler(ServiceUnavailable)
async def unavailable_handler(_: Request, exc: ServiceUnavailable):
    return JSONResponse(status_code=503, content={"error": {"code": "SERVICE_UNAVAILABLE", "message": str(exc)}})

@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    logger.exception("Unhandled API error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected internal error occurred."}})
