from __future__ import annotations
from functools import lru_cache
from typing import Generator
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from .config import Settings, get_settings
from .services.mock import MockWellService, MockKnowledgeService, MockPredictionService, MockAlertService, MockRecommendationService, MockRealtimeService


@lru_cache
def get_session_factory(settings: Settings = Depends(get_settings)):
    engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    settings = get_settings()
    if not settings.enable_database:
        raise RuntimeError("Database access is disabled. Set NWIS_ENABLE_DATABASE=true for database mode.")
    session_factory = get_session_factory(settings)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def get_well_service():
    settings = get_settings()
    if settings.enable_database:
        from .services.database import DatabaseWellService
        session_factory = get_session_factory(settings)
        session = session_factory()
        try:
            yield DatabaseWellService(session)
        finally:
            session.close()
    else:
        yield MockWellService()


@lru_cache
def _knowledge_service():
    return MockKnowledgeService()


def get_knowledge_service(): return _knowledge_service()

@lru_cache
def _prediction_service(): return MockPredictionService()

def get_prediction_service(): return _prediction_service()

@lru_cache
def _alert_service(): return MockAlertService()

def get_alert_service(): return _alert_service()

@lru_cache
def _recommendation_service(): return MockRecommendationService()

def get_recommendation_service(): return _recommendation_service()

@lru_cache
def _realtime_service(): return MockRealtimeService()

def get_realtime_service(): return _realtime_service()
