from fastapi import FastAPI

from .api import build_router
from .config import get_settings
from .factory import create_ertmac_adapter


def create_app() -> FastAPI:
    """Create a standalone development FastAPI application for real-time NWIS."""
    settings = get_settings()
    app = FastAPI(title="NWIS eRTMAC Integration", version="1.0.0")
    app.include_router(build_router(create_ertmac_adapter(settings), settings=settings))
    return app


app = create_app()
