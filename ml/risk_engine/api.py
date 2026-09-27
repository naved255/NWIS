from __future__ import annotations
from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .engine import RiskPredictionEngine

class PredictionRequest(BaseModel):
    features: Dict[str, Any]


def create_app(artifact_dir: str = "artifacts/risk_engine") -> FastAPI:
    """Create a small FastAPI adapter for integration with the NWIS backend."""
    app = FastAPI(title="NWIS Drilling Risk Engine", version="1.0.0")
    engine = RiskPredictionEngine.load(artifact_dir)

    @app.get("/health")
    def health():
        return {"status": "ok", "model_version": engine.model_version, "risk_type": engine.risk_type}

    @app.post("/predict")
    def predict(request: PredictionRequest):
        try:
            return engine.predict_risk(request.features).model_dump()
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app
