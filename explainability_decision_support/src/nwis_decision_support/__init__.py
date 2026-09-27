"""NWIS Explainable AI and Decision Support module."""
from .explainability.service import explain_prediction
from .explainability.models import FeatureContribution, ExplanationResult
from .alerts.service import generate_alert
from .alerts.models import AlertContext, AlertResult, AlertRule
from .recommendations.service import generate_recommendation
from .recommendations.models import EvidenceItem, RecommendationContext, RecommendationResult

__all__ = [
    "explain_prediction", "FeatureContribution", "ExplanationResult",
    "generate_alert", "AlertContext", "AlertResult", "AlertRule",
    "generate_recommendation", "EvidenceItem", "RecommendationContext", "RecommendationResult",
]
