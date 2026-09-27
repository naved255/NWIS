"""Optional FastAPI router. Import only when FastAPI is installed."""
from fastapi import APIRouter
from ..alerts.models import AlertContext, AlertRule, AlertResult
from ..alerts.service import generate_alert
from ..recommendations.models import RecommendationContext, RecommendationResult
from ..recommendations.service import generate_recommendation

router = APIRouter(prefix="/api/v1/decision-support", tags=["decision-support"])

@router.post("/alerts", response_model=AlertResult)
def create_alert(context: AlertContext, rules: list[AlertRule] | None = None):
    return generate_alert(context, rules)

@router.post("/recommendations", response_model=RecommendationResult)
def create_recommendation(context: RecommendationContext):
    return generate_recommendation(context)
